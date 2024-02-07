import os

from flask import Flask, render_template, request, flash, redirect, session, g, url_for
from flask_debugtoolbar import DebugToolbarExtension
import requests
from sqlalchemy.exc import IntegrityError

from forms import UserAddForm, LoginForm, UserEditForm, SearchForm
from models import db, connect_db, User, Garden, Plant, GardenPlant

CURR_USER_KEY = "curr_user"
# API_SECRET_ID=os.getenv('x-permapeople-key-id')
# API_SECRET_KEY=os.getenv('x-permapeople-key-secret')
API_SECRET_ID=os.getenv('SECRET_API_ID')
API_SECRET_KEY=os.getenv('SECRET_API_KEY')
API_HEADERS={"x-permapeople-key-id": API_SECRET_ID,
        "x-permapeople-key-secret": API_SECRET_KEY}

BASE_URL = "https://permapeople.org/api"


app = Flask(__name__)

# Get DB_URI from environ variable (useful for production/testing) or,
# if not set there, use development local db.
app.config['SQLALCHEMY_DATABASE_URI'] = (
    os.environ.get('DATABASE_URL', 'postgresql:///plantify'))

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = False
# app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = True
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', "issa secret")
toolbar = DebugToolbarExtension(app)

connect_db(app)
db.create_all()


##############################################################################
# User signup/login/logout


@app.before_request
def add_user_to_g():
    """If we're logged in, add curr user to Flask global."""

    if CURR_USER_KEY in session:
        g.user = User.query.get(session[CURR_USER_KEY])

    else:
        g.user = None


def do_login(user):
    """Log in user."""

    session[CURR_USER_KEY] = user.id


def do_logout():
    """Logout user."""

    if CURR_USER_KEY in session:
        del session[CURR_USER_KEY]


@app.route('/', methods=['GET', 'POST'])
def homepage():
    """Show homepage:

    - anon users: no messages
    - logged in: 100 most recent messages of followed_users
    """

    form = SearchForm()

    # if g.user:
    #     following = [f.id for f in g.user.following] + [g.user.id]
    return render_template('home.html', form=form)