import os

from flask import Flask
from flask.json import jsonify

from models.Contextual import Contextual
from models import Collaborative
from models import Conversion


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)

    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'flaskr.sqlite'),
        CORS_HEADERS='Content-Type'
    )

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    cont = Contextual()

    @app.route('/recommendation/<movie>')
    def get_recommendation(movie):
        return jsonify({'results': cont.get_rec_json(cont.get_recommendations(movie))})

    @app.route('/top')
    def get_top():
        return jsonify({'results': cont.get_rec_json(cont.get_first_movies(10))})

    @app.route('/for_me/<int:userId>')
    def get_for_me(userId):
        pr = Collaborative.predict(userId)

        uids = []
        for (mid, rating) in pr:
            imdb_id = Conversion.getImdbId(mid)
            if imdb_id != -1:
                uids.append(int(imdb_id))
        return jsonify({'results': cont.get_rec_json_imdb(uids)})

    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
        return response

    return app
