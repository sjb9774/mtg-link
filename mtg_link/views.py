from mtg_link import app
from flask import render_template, jsonify, request, send_from_directory, abort
from flask import redirect
from mtg_link.models.magic import MtgCardModel, MtgCardSetModel
from mtg_link.models.users import User
from mtg_link.models.sessions import Session
from mtg_link.utils.search import get_card_suggestions
from mtg_link.utils.users import login, get_active_user, hash_password, create_user
from jinja2 import TemplateNotFound
import json
import db

@app.route('/', methods=['GET'])
def home():
    active_user = get_active_user()
    if not active_user: # no user is logged in
        return redirect('/login', code=302)
    else:
        return render_template('/views/view_home.html', active_user=active_user)

@app.route('/login', methods=['GET'])
def login_page():
    active_user = get_active_user()
    return render_template('views/view_login.html', active_user=active_user)

@app.route('/api/card', methods=['GET'])
def api_get_card():
    args = request.args.to_dict()
    if not args:
        # TODO: Return a nice page detailing how to use the api
        return 'Needs some arguments!'
    else:
        filtered_args = {kw: args[kw] for kw in args if kw in MtgCardModel.__fields__}
        cards = MtgCardModel.filter_by(**filtered_args).all()
        return jsonify({'cards':[dict(card) for card in cards]})

@app.route('/view/card', methods=['GET'])
def view_card():
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
        return render_template("views/view_card.html", card=card, active_user=get_active_user())
    else:
        return fourfour_wrapper(args.get('name'))

@app.errorhandler(404)
def four_o_four(err):
    return render_template('views/404.html', suggestions=None), 404

def fourfour_wrapper(card_name):
    active_user = get_active_user()
    suggestions = get_card_suggestions(card_name)
    if len(suggestions) == 1:
        return render_template("views/view_card.html", card=suggestions[0], active_user=active_user)
    else:
        return render_template('views/404.html', suggestions=suggestions, active_user=active_user), 404

@app.route('/image', methods=['GET'])
def image():
    args = request.args.to_dict()
    q = db.Session.query(MtgCardModel).join(MtgCardSetModel).filter(MtgCardSetModel.code==args.get('set')) if args.get('set') else MtgCardModel
    card = q.filter(MtgCardModel.name == args.get('name')).first()
    return send_from_directory('/home/myaccount/Pictures', '{card.set.code}/{card.name} - {card.multiverse_id}.png'.format(card=card))

@app.route('/search', methods=['GET'])
def search():
    args = request.args.to_dict()
    return jsonify({'url': '/view/card?name={}'.format(args.get('name')), 'success': True})

@app.route('/api/login', methods=['POST'])
def user_login():
    args = request.form.to_dict()
    result = {'success': False}
    if args.get('username') and args.get('password'):
        session = login(args.get('username'), args.get('password'))
        if session:
            result['success'] = True
            result['session_id'] = session.id
    return jsonify(result)

@app.route('/api/logout', methods=['POST'])
def user_logout():
    args = request.form.to_dict()
    sess = Session.get(args.get('sessionId', ''))
    if sess and sess.active:
        sess.active = False
        return jsonify({'success': True})
    else:
        return jsonify({'success': False})

@app.route('/api/register', methods=['POST'])
def user_register():
    args = request.form.to_dict()
    user = create_user(args.get('username'), args.get('password'))
    user.insert()
    db.Session.commit()
    return jsonify({'success': True})


@app.route('/account/<username>', methods=['GET'])
def account(username):
    active_user = get_active_user()
    user = User.filter_by(username=username).first()
    return render_template('views/view_account.html', user=user, active_user=active_user)
