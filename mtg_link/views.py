from mtg_link import app
from flask import render_template, jsonify, request, send_from_directory, abort
from flask import redirect
from mtg_link.models.magic import MtgCardModel, MtgCardSetModel
from mtg_link.models.users import User
from mtg_link.models.sessions import Session
from mtg_link.models.decks import Deck
from mtg_link.utils.search import get_card_suggestions
from mtg_link.utils.users import login, get_active_user, hash_password, create_user
from mtg_link.utils.decks import create_deck
from mtg_link.utils.views import custom_route, custom_render
from jinja2 import TemplateNotFound
import json
import db

@custom_route('/', methods=['GET'])
def home(get_args):
    if not get_active_user():
        return redirect('/login', code=302)
    else:
        return custom_render('/views/view_home.html')

@custom_route('/login', methods=['GET'])
def login_page(get_args):
    return custom_render('views/view_login.html')

@custom_route('/api/card', methods=['GET'])
def api_get_card(get_args):
    if not args:
        # TODO: Return a nice page detailing how to use the api
        return 'Needs some arguments!'
    else:
        filtered_args = {kw: args[kw] for kw in args if kw in MtgCardModel.__fields__}
        cards = MtgCardModel.filter_by(**filtered_args).all()
        return jsonify({'cards':[dict(card) for card in cards]})

@custom_route('/view/card', methods=['GET'])
def view_card(get_args):
    args = request.args.to_dict()
    q = db.Session.query(MtgCardModel).join(MtgCardSetModel)\
                                      .filter(MtgCardModel.name == args.get('name'))\
                                      .filter(MtgCardModel.multiverse_id != None)
    if args.get('set'):
        q = q.filter(MtgCardSetModel.code==args.get('set'))
    else:
        q = q.order_by(MtgCardSetModel.release_date.desc())

    card = q.first()
    if card:
        return custom_render("views/view_card.html", card=card)
    else:
        return custom_render("views/view_card_suggestions.html", suggestions=get_card_suggestions(args.get('name')))

@app.errorhandler(404)
def four_o_four(err):
    return custom_render('views/404.html'), 404

@custom_route('/image', methods=['GET'])
def image(get_args):
    set_code = get_args.get('set')
    name = get_args.get('name')
    q = db.Session.query(MtgCardModel).join(MtgCardSetModel).filter(MtgCardSetModel.code==set_code) if set_code else MtgCardModel
    card = q.filter(MtgCardModel.name == name).filter(MtgCardModel.multiverse_id != None).first()
    return send_from_directory('/home/myaccount/Pictures', '{card.set.code}/{card.name} - {card.multiverse_id}.png'.format(card=card))

@custom_route('/search', methods=['GET'])
def search(get_args):
    name = get_args.get('name')
    card = MtgCardModel.filter_by(name=name).first()
    result = {
        'success': False
    }
    if card:
        result['success'] = True
        result['url'] = '/view/card?name={name}'.format(name=card.name)
        result['imageUrl'] = '/image?name={name}'.format(name=card.name)
    else:
        result['success'] = False
        result['url'] = '/view/card?name={name}'.format(name=name)

    return jsonify(result)

@custom_route('/api/login', methods=['POST'])
def user_login(post_args):
    result = {'success': False}
    if post_args.get('username') and post_args.get('password'):
        session = login(post_args.get('username'), post_args.get('password'))
        if session:
            result['success'] = True
            result['session_id'] = session.id
    return jsonify(result)

@custom_route('/api/logout', methods=['POST'])
def user_logout(post_args):
    sess = Session.get(post_args.get('sessionId', ''))
    if sess and sess.active:
        sess.active = False
        return jsonify({'success': True})
    else:
        return jsonify({'success': False})

@custom_route('/api/register', methods=['POST'])
def user_register(post_args):
    user = create_user(post_args.get('username'), post_args.get('password'))
    user.insert()
    db.Session.commit()
    return jsonify({'success': True})

@custom_route('/api/new-deck', methods=['POST'])
def save_new_deck(post_args):
    deck_text = post_args.get('text').split('\n')
    active_user = get_active_user()
    deck, xcards = create_deck(deck_text)
    deck.user_id = active_user.id
    deck.name = post_args.get('deckName')
    deck.insert()
    for xcard in xcards:
        xcard.insert()
    db.Session.commit()

    return jsonify({'success': True, 'deckName': deck.name})

@custom_route('/account/<username>', methods=['GET'])
def account(username, get_args):
    user = User.filter_by(username=username).first()
    return custom_render('views/view_account.html', user=user)

@custom_route('/view/new-deck', methods=['GET'])
def new_deck(get_args):
    return custom_render('views/view_new_deck.html')

@custom_route('/view/decks/<username>', methods=['GET'])
def view_users_decks(username, get_args):
    user = User.filter_by(username=username).first()
    if user:
        return custom_render('views/view_decks.html', user=user)
    else:
        abort(404)

@custom_route('/view/decks/<username>/<deck>', methods=['GET'])
def view_deck(username, deck, get_args):
    from collections import OrderedDict
    user = User.filter_by(username=username).first()
    deck = Deck.filter_by(user_id=user.id, name=deck).first()
    deck_dict = OrderedDict()

    priority_list = [
        'lands',
        'creatures',
        'artifacts',
        'enchantments',
        'planeswalkers',
        'instants',
        'sorceries'
    ]

    for card_type in priority_list:
        deck_dict.setdefault(card_type, [])
        for card, quantity in getattr(deck, card_type):
            already_added = False
            for ctype in priority_list[:priority_list.index(card_type)]:
                if (card, quantity) in deck_dict[ctype]:
                    already_added = True
                    break
            if not already_added:
                deck_dict[card_type].append((card, quantity))

    return custom_render('/views/view_deck.html', user=user, deck=deck, deck_dict=deck_dict)
