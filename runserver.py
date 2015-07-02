if __name__ == "__main__":
    from mtg_link import app
    from mtg_link.views import *
    app.run(debug=True, host='127.0.0.1', port=5000)
