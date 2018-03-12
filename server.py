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
    matches = db.Column(db.Integer, default=0)
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

    # load 2 different, random players from db - first one with less matches
    player_context = [__get_random_player(match_threshold=35), __get_random_player()]
    while player_context[0].id == player_context[1].id:
        player_context[1] = __get_random_player()

    if session.new:
        session['player_store'] = [x.id for x in player_context]

    if buttonForm.is_submitted():
        choice = int(buttonForm.choice.data)
        winner_id = session['player_store'][choice-1]
        loser_id = session['player_store'][choice-2]

        winner = Player.query.get(winner_id)
        loser = Player.query.get(loser_id)

        # print "[USER VOTED]: winner %s - loser: %s" % (winner, loser)
        winner, loser = elo.match(winner, loser)
        db.session.commit()

    session['player_store'] = [x.id for x in player_context]


    return render_template('main.html', players=player_context, form=buttonForm)

def __get_random_player(match_threshold=None):
    # load a random player from database
    # match_threshold is between 0 and 100
    count = Player.query.count()
    if match_threshold:
        rand = random.randint(0, int(count*0.01*match_threshold))
        pl = Player.query.order_by(Player.matches.asc())[rand]
    else:
        rand = random.randrange(1, count+1)
        pl = Player.query.get(rand)

    return pl

@app.route("/ranking/<int:limit>")
def ranking(limit):
    limit = min(limit, 100)
    top = Player.query.order_by(Player.score.desc()).limit(limit).all()
    # print sorted([p.score for p in top])
    return render_template('ranking.html', players=top)

@app.route("/player/<id>")
def player_details(id):
    player = Player.query.filter_by(id=id).first()
    return render_template('overview.html', player=player)

@app.errorhandler(404)
def page_not_found(e):
    return render_template('error.html', message="sorry, your are wrong: %s" % e, code=404), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('error.html', message=e, code=500), 500

# forms
class ButtonForm(FlaskForm):
    choice = HiddenField("choice")
    submit = SubmitField("Vote")

if __name__ == '__main__':
    app.run(host='0.0.0.0')
