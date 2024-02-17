"""SQLAlchemy models for Warbler."""

from datetime import datetime

from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy

herbs = ['Anise Hyssop','Basil','Bay Laurel','Calendula','Chamomile','Chives','Cilantro','Coriander',
 'Cumin','Dill','Echinacea','Fennel','Feverfew','Lavender','Lemon Balm','Marigold','Marjoram','Mint',
 'Oregano','Parsley','Rosemary','Sage','Stevia','Summer Savory','Tarragon','Thyme','Winter Savory']

bcrypt = Bcrypt()
db = SQLAlchemy()


class Favorites(db.Model):
    """Mapping user favorites to warbles."""

    __tablename__ = 'favorites' 

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id', ondelete='cascade')
    )

    garden_id = db.Column(
        db.Integer,
        db.ForeignKey('gardens.id', ondelete='cascade'),
        unique=True
    )


class User(db.Model):
    """User in the system."""

    __tablename__ = 'users'

    id = db.Column(
        db.Integer,
        primary_key=True,
    )

    username = db.Column(
        db.Text,
        nullable=False,
        unique=True,
    )

    image_url = db.Column(
        db.Text,
        default="/static/images/default-pic.png",
    )

    password = db.Column(
        db.Text,
        nullable=False,
    )

    gardens = db.relationship('Garden')

    def __repr__(self):
        return f"<User #{self.id}: {self.username}>"


    @classmethod
    def signup(cls, username, password, image_url):
        """Sign up user.

        Hashes password and adds user to system.
        """

        hashed_pwd = bcrypt.generate_password_hash(password).decode('UTF-8')

        user = User(
            username=username,
            password=hashed_pwd,
            image_url=image_url,
        )

        db.session.add(user)
        return user

    @classmethod
    def authenticate(cls, username, password):
        """Find user with `username` and `password`.

        This is a class method (call it on the class, not an individual user.)
        It searches for a user whose password hash matches this password
        and, if it finds such a user, returns that user object.

        If can't find matching user (or if password is wrong), returns False.
        """

        user = cls.query.filter_by(username=username).first()

        if user:
            is_auth = bcrypt.check_password_hash(user.password, password)
            if is_auth:
                return user

        return False
    
    # plants = db.relationship('Plant', secondary='gardens_plants', backref='gardens')


class Plant(db.Model):
    """An individual plant"""

    __tablename__ = 'plants'

    id = db.Column(
        db.Integer,
        primary_key=True,
        unique=True,
    )
    
    name = db.Column(
        db.String,
        nullable=False,
    )

    api_id = db.Column(
        db.Integer,
        nullable=False,
        unique=True,
    )


class Garden(db.Model):
    """A Garden group"""

    __tablename__ = 'gardens'

    id = db.Column(
        db.Integer,
        primary_key=True,
    )

    name = db.Column(
        db.String,
        nullable=False,
    )

    description = db.Column(
        db.String(140),
        default=""
    )

    image_url = db.Column(
        db.Text,
        default="/static/images/garden-default.jpg",
    )

    created_at = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow(),
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id', ondelete='CASCADE'),
        nullable=False,
    )

    user = db.relationship('User')
    plants = db.relationship('Plant', secondary='gardens_plants', backref='gardens')


class GardenPlant(db.Model):
   """Mapping of a plant to a garden."""

   __tablename__ = 'gardens_plants'

   id = db.Column(
       db.Integer, 
       primary_key=True, 
       autoincrement=True,
       )
   
   garden_id = db.Column(
       db.Integer,
       db.ForeignKey('gardens.id'),
       )
   
   plant_id = db.Column(
       db.Integer, 
       db.ForeignKey('plants.api_id'),
       )


def connect_db(app):
    """Connect this database to provided Flask app.

    You should call this in your Flask app.
    """

    db.app = app
    db.init_app(app)
   # app.app_context().push()
