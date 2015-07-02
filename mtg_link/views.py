from mtg_link import app

@app.route('/', methods=['GET'])
def home():
    return 'Hello world!'
