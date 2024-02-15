import os

from flask import Flask, render_template, request, flash, redirect, session, g, url_for
from flask_debugtoolbar import DebugToolbarExtension
import requests
from sqlalchemy.exc import IntegrityError

from forms import UserAddForm, LoginForm, UserEditForm, SearchForm, GardenAddForm, PlantToGardenForm
from models import db, connect_db, User, Garden, Plant, GardenPlant

CURR_USER_KEY = "curr_user"
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


@app.route('/signup', methods=["GET", "POST"])
def signup():
   """Handle user signup.

   Create new user and add to DB. Redirect to home page.

   If form not valid, present form.

   If there already is a user with that username: flash message
   and re-present form.
   """

   form = UserAddForm()

   if form.validate_on_submit():
      try:
         user = User.signup(
               username=form.username.data,
               password=form.password.data,
               # email=form.email.data,
               image_url=form.image_url.data or User.image_url.default.arg,
         )
         db.session.commit()

      except IntegrityError:
         flash("Username already taken", 'danger')
         return render_template('users/signup.html', form=form)

      do_login(user)

      return redirect("/")

   else:
      return render_template('users/signup.html', form=form)


@app.route('/login', methods=["GET", "POST"])
def login():
   """Handle user login."""

   form = LoginForm()

   if form.validate_on_submit():
      user = User.authenticate(form.username.data,
                              form.password.data)

      if user:
         do_login(user)
         flash(f"Hello, {user.username}!", "success")
         return redirect("/")

      flash("Invalid credentials.", 'danger')

   return render_template('users/login.html', form=form)


@app.route('/logout')
def logout():
   """Handle logout of user."""

   # IMPLEMENT THIS
   do_logout()

   flash("You have logged out!", "info")
   return redirect("/login")


##############################################################################
# General User routes:

@app.route('/users')
def list_users():
   """Page with listing of users.

   Can take a 'q' param in querystring to search by that username.
   """

   search = request.args.get('q')

   if not search:
      users = User.query.all()
   else:
      users = User.query.filter(User.username.like(f"%{search}%")).all()

   return render_template('users/index.html', users=users)


@app.route('/users/<int:user_id>')
def user_show(user_id):
   """Show user profile."""

   user = User.query.get_or_404(user_id)

   # snagging messages in order from the database;
   # user.messages won't be in order by default
   users = (User
               .query
               .filter(User.id == user_id)
               # .order_by(User.created_at.desc())
               .limit(100)
               .all())
   return render_template('users/show.html', user=user)


##############################################################################
# Plant routes:


@app.route('/plants')
def list_plants():
   """Page with listing of plants.

   Can take a 'q' param in querystring to search by that username.
   """

   # search = request.args.get('q')

   # if not search:
   #     plants = Plant.query.all()
   # else:
   #     plants = User.query.filter(User.username.like(f"%{search}%")).all()

   search = request.args.get('q')

   if not search:
      resp = requests.get(f"{BASE_URL}/plants",
                           headers=API_HEADERS
                           ).json()
   else:
      resp = requests.post(f"{BASE_URL}/search",
                           headers=API_HEADERS,
                           params={"q": search}
                           ).json()
   
   plants = resp['plants']
   # flash(API_HEADERS)
   # flash(plants)
   flash(plants[-1]['id'])

   return render_template('plants/index.html', plants=plants)


@app.route('/plants/<int:plant_id>', methods=["GET", "POST"])
def plant_show(plant_id):
   """Show plant profile."""

   # if g.user:
   #    form = PlantToGardenForm()
   #    gardens = [(g.id, g.name) for g in Garden.query.all()]
   #    form.gardens.choices = gardens

   resp = requests.get(f"{BASE_URL}/plants/{plant_id}",
                           headers=API_HEADERS
                           )
   
   plant=resp.json()

   plant_data={}

   for info in plant['data']:
      plant_data[f"{info['key']}"]=(f"{info.get('value')}")

   flash(f"{plant_data['Wikipedia']}", 'info')
   # flash(f"{plant['data'][3]['key']}", 'info')
   
   # if g.user:
   #    return render_template('plants/show.html', plant=plant, plant_data=plant_data, form=form)

   # if request.method == 'POST':

   
   return render_template('plants/show.html', plant=plant, plant_data=plant_data)


@app.route('/plants/<int:plant_id>/add', methods=["POST"])
def add_plant_to_garden(plant_id):



   return redirect('/plants/<int:plant_id>')




##############################################################################
# Garden routes:

@app.route('/gardens')
def list_gardens():
   """Page with listing of gardens.

   Can take a 'q' param in querystring to search by that gardenname.
   """

   search = request.args.get('q')

   if not search:
      gardens = Garden.query.all()
   else:
      gardens = Garden.query.filter(Garden.name.like(f"%{search}%")).all()

   return render_template('gardens/index.html', gardens=gardens)


@app.route('/gardens/<int:garden_id>')
def garden_show(garden_id):
   """Show garden profile."""

   garden = Garden.query.get_or_404(garden_id)
   # user = User.query.get_or_404(garden.user_id)

   # snagging messages in order from the database;
   # user.messages won't be in order by default
   # gardens = (Garden
   #             .query
   #             .filter(Garden.user_id == user_id)
   #             .order_by(Garden.created_at.desc())
   #             .limit(100)
   #             .all())
   plants=[]
   for plant in garden.plants:
      resp = requests.get(f"{BASE_URL}/plants/{plant.api_id}",
                           headers=API_HEADERS
                           )
      json = resp.json()
      plants.append(json)

   return render_template('gardens/show.html', garden=garden, plants=plants)


@app.route('/gardens/<int:garden_id>/edit')
def garden_edit(garden_id):
   """Edit Garden Information"""

   if not g.user:
      flash("Access unauthorized.", "danger")
      return redirect("/")

   garden = Garden.query.get_or_404(garden_id)

   if g.user.id != garden.user_id:
      flash("You do not have permission to do that", 'danger')
      return redirect('/gardens/<int:garden_id>')

   form = GardenAddForm()

   if form.validate_on_submit():
      user = User.authenticate(form.username.data,
                              form.password.data)

      if user:
         try:
            garden.name = form.name.data
            db.session.commit()
            flash(f"Garden renamed to {garden.name}", "success")
            return redirect("/gardens/<int:garden_id>")
         
         except IntegrityError:
            flash("Garden name already taken", 'warning')
            return render_template('users/update.html', form=form)

      flash("Invalid credentials.", 'danger')

   return render_template('users/login.html', form=form)


###### TODO: Delete Garden



# conversion=round(requests.get(f"{BASE_URL}/convert",
   #                           params={"access_key": API_SECRET_KEY,
   #                                   "from": from_curr,
   #                                   "to": to_curr,
   #                                   "amount": amount}).json()['result'], 2)
   #     return render_template("converted.html", conversion=conversion)