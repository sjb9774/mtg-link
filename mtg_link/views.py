from mtg_link import app
from flask import render_template, jsonify, request, send_from_directory
from mtg_link.models.magic import MtgCardModel, MtgCardSetModel
import json

@app.route('/', methods=['GET'])
def home():
    return render_template('readme.html')

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
    card = MtgCardModel.filter_by(name=args.get('name')).first()
    if card:
        print card.name
        return render_template("views/view_card.html", card=card)
    else:
        return None

@app.route('/image', methods=['GET'])
def image():
    args = request.args.to_dict()
    card = MtgCardModel.filter_by(name=args.get('name')).first()
    return send_from_directory('/home/myaccount/Pictures', '{card.set.code}/{card.name} - {card.multiverse_id}.png'.format(card=card))
