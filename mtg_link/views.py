from mtg_link import app
from flask import render_template, jsonify, request
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
