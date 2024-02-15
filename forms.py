from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField, SelectField
from wtforms.validators import DataRequired, Length


class GardenAddForm(FlaskForm):
    """Form for adding/editing Gardens."""

    name = TextAreaField('Enter Garden Name', validators=[DataRequired()])


class PlantToGardenForm(FlaskForm):
    """Form for adding/editing Gardens."""

    gardens = SelectField('Select Garden', validators=[DataRequired()])


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
    # bio = TextAreaField('Add Bio')
    password = PasswordField('Password', validators=[Length(min=6)])

class SearchForm(FlaskForm):
    """Main plant search bar."""

    query = StringField('Search for a Plant or Garden', validators=[DataRequired()])