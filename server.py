#-*- coding:utf-8 -*-
'''
    python server.py runserver

    creates the flask app, and hosts it for any device on the same network
'''
from flask import Flask, render_template, session, url_for
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_script import Manager, Shell
from flask_wtf import FlaskForm

from wtforms.fields.simple import SubmitField, HiddenField

from elo import Elo

import os
from datetime import datetime
import random

basedir = os.path.abspath(os.path.dirname(__file__))

# detect whether app is being run from terminal
# for execution, if __name__ == '__main__': app.run(port=4995)
app = Flask(__name__)

# set a secure secret key so that flask can use cookies for sessions
app.config['SECRET_KEY'] = '169d7c24b62bb17eafcc2bcded23e888'

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'database.sqlite')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True

manager = Manager(app)
bootstrap = Bootstrap(app)
db = SQLAlchemy(app)
elo = Elo()

# database model definition
class Player(db.Model):
    __tablename__ = 'player'
    id = db.Column(db.Integer, primary_key=True, index=True)
    name = db.Column(db.Unicode(64), nullable=False)
    score = db.Column(db.Float, default=1500.00)
    wins = db.Column(db.Integer, default=0)
    imgurl = db.Column(db.Unicode(254))
    added = db.Column(db.DateTime, default=datetime.now())

    def __repr__(self):
        return "<Player %s>" % self.id

    @property
    def image(self):
        fn = "compare/%s" % self.imgurl
        return url_for('static', filename=fn)

# views (supported HTTP methods: both GET and POST request)
@app.route("/", methods=['GET', 'POST'])
def mainpage():
    buttonForm = ButtonForm()

    # load all players
    n = Player.query.count()
    player_context = Player.query.all()

    if session.new:
        session['player_store'] = [x.id for x in player_context]

    if buttonForm.is_submitted():
        choice = int(buttonForm.choice.data)
        winner_id = session['player_store'][choice - 1]
        loser_ids = [session['player_store'][i] for i in xrange(n) if i != choice - 1]

        winner = Player.query.get(winner_id)
        losers = [Player.query.get(loser_id) for loser_id in loser_ids]

        # print "Winner - %s" % winner
        elo.update(winner=winner, losers=losers)
        db.session.commit()

    player_context = Player.query.order_by(Player.score.desc()).all()
    session['player_store'] = [x.id for x in player_context]

    return render_template('main.html', players=player_context, form=buttonForm)

@app.route("/ranking/<int:limit>")
def ranking(limit):
    limit = min(limit, 100)
    ord_players = Player.query.order_by(Player.score.desc()).limit(limit).all()
    return render_template('ranking.html', players=ord_players)

@app.route("/player/<id>")
def player_details(id):
    player = Player.query.filter_by(id=id).first()
    return render_template('overview.html', player=player)

@app.errorhandler(404)
def page_not_found(e):
    return render_template('error.html', message="Mistyped? %s" % e, code=404), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('error.html', message=e, code=500), 500

# forms
class ButtonForm(FlaskForm):
    choice = HiddenField("choice")
    submit = SubmitField("Buy")

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
