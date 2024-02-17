from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField, SelectField
from wtforms.validators import DataRequired, Length


class GardenAddForm(FlaskForm):
    """Form for adding/editing Gardens."""

    name = StringField('Garden Name', validators=[DataRequired()])
    description = StringField('Garden description')


class PlantToGardenForm(FlaskForm):
    """Form for adding/editing Gardens."""

    gardens = SelectField('', validate_choice=False)


class UserAddForm(FlaskForm):
    """Form for adding users."""

    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[Length(min=6)])
    # image_url = StringField('(Optional) Image URL')


class LoginForm(FlaskForm):
    """Login form."""

    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[Length(min=6)])

class UserEditForm(FlaskForm):
    """Form for editing users."""

    username = StringField('Username', validators=[DataRequired()])
    image_url = StringField('(Optional) Image URL')
    # password = PasswordField('Password', validators=[Length(min=6)])

class SearchForm(FlaskForm):
    """Main plant search bar."""

    query = StringField('Search for a Plant or Garden', validators=[DataRequired()])