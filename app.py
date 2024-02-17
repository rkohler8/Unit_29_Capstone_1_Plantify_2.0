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


@app.route('/users/edit', methods=["GET", "POST"])
def profile():
    """Update profile for current user."""

    # IMPLEMENT THIS
    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")
    
    form = UserEditForm(obj=g.user)
    
    if form.validate_on_submit():
        if User.authenticate(g.user.username,
                                 form.password.data):
            g.user.username=form.username.data
            g.user.image_url=form.image_url.data or "/static/images/default-pic.png"

            db.session.commit()
            return redirect(f"/users/{g.user.id}")


        flash("Invalid credentials.", 'danger')
        return redirect("/")

    return render_template('users/edit.html', form=form)


@app.route('/users/delete', methods=["POST"])
def delete_user():
    """Delete user."""

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    do_logout()

    db.session.delete(g.user)
    db.session.commit()

    return redirect("/signup")


##############################################################################
# Plant routes:


@app.route('/plants')
def list_plants():
   """Page with listing of plants.

   Can take a 'q' param in querystring to search by any Plant parameter.
   """

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

   if g.user:
      form = PlantToGardenForm()
      gardens = [(g.id, g.name) for g in Garden.query.all()]
      # flash(f"{gardens}")
      form.gardens.choices = gardens


   resp = requests.get(f"{BASE_URL}/plants/{plant_id}",
                           headers=API_HEADERS
                           )
   
   plant=resp.json()

   plant_data={}

   for info in plant['data']:
      plant_data[f"{info['key']}"]=(f"{info.get('value')}")


   if form.validate_on_submit():
      gar = form.gardens.data
      # flash(f'{gar}')
      garden = Garden.query.get_or_404(gar)
      for p in garden.plants:
         if p.id == plant_id:
            flash(f"Plant already in garden '{garden.name}'", 'warning')
            return render_template('plants/show.html', plant=plant, plant_data=plant_data, form=form)

      temp_plant = Plant.query.filter_by(api_id=plant['id']).all()
      if len(temp_plant) == 0:
         new_plant = Plant(id=plant_id,
                           name=plant['name'],
                           api_id=plant['id'])
         db.session.add(new_plant)
         db.session.commit()
         new_link = GardenPlant(garden_id=garden.id,
                              plant_id=plant_id)
         db.session.add(new_link)
         db.session.commit()
         flash(f"new Plant '{plant['name']}' added to garden '{garden.name}'", 'info')
         return redirect(f'/plants/{plant_id}')
      else: 
         new_link = GardenPlant(garden_id=garden.id,
                              plant_id=plant_id)
         db.session.add(new_link)
         db.session.commit()
         flash(f"Plant '{plant['name']}' already localized, added to garden '{garden.name}'", 'info')
         return redirect(f'/plants/{plant_id}')


   # else:
   #    flash(f"fail", 'warning')

   # flash(f"{plant_data['Wikipedia']}", 'info')
   # flash(f"{plant['data'][3]['key']}", 'info')
   
   if g.user:
      return render_template('plants/show.html', plant=plant, plant_data=plant_data, form=form)

   return render_template('plants/show.html', plant=plant, plant_data=plant_data)


@app.route('/plants/<int:plant_id>/add/<int:garden_id>', methods=["POST"])
def add_plant_to_garden(plant_id):



   return redirect('/plants/<int:plant_id>')




##############################################################################
# Garden routes:

@app.route('/gardens')
def list_gardens():
   """Page with listing of gardens.

   Can take a 'q' param in querystring to search by that garden name.
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

   plants=[]
   for plant in garden.plants:
      resp = requests.get(f"{BASE_URL}/plants/{plant.api_id}",
                           headers=API_HEADERS
                           )
      json = resp.json()
      plants.append(json)

   return render_template('gardens/show.html', garden=garden, plants=plants)


@app.route('/gardens/new', methods=["GET", "POST"])
def garden_add():
    """Add a garden:

    Show form if GET. If valid, update message and redirect to user page.
    """

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    form = GardenAddForm()

    if form.validate_on_submit():
        gar = Garden(name=form.name.data,
                     user_id=g.user.id,
                     description=form.description.data or None
                     )
        g.user.gardens.append(gar)
        db.session.commit()

        return redirect(f"/users/{g.user.id}")

    return render_template('gardens/new.html', form=form)


@app.route('/gardens/<int:garden_id>/edit', methods=["GET", "POST"])
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

      if g.user:
         try:
            garden.name = form.name.data
            db.session.commit()
            flash(f"Garden renamed to {garden.name}", "success")
            return redirect(f'/gardens/{garden_id}')
         
         except IntegrityError:
            flash("Garden name already taken", 'warning')
            return render_template('gardens/edit.html', form=form)

      flash("Invalid credentials.", 'danger')

   return render_template('gardens/edit.html', form=form)


###### TODO: Delete Garden
@app.route('/gardens/<int:garden_id>/delete', methods=["POST"])
def garden_delete(garden_id):
    """Delete a garden."""

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    gar = Garden.query.get(garden_id)
    db.session.delete(gar)
    db.session.commit()

    flash(f"Garden '{gar.name}' Deleted", 'warning')

    return redirect(f"/users/{g.user.id}")



# conversion=round(requests.get(f"{BASE_URL}/convert",
   #                           params={"access_key": API_SECRET_KEY,
   #                                   "from": from_curr,
   #                                   "to": to_curr,
   #                                   "amount": amount}).json()['result'], 2)
   #     return render_template("converted.html", conversion=conversion)