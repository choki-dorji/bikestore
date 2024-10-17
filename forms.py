from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm  # Import FlaskForm
from wtforms import EmailField, PasswordField, StringField, SubmitField, IntegerField, DateField, FloatField, FileField, TextAreaField # Import StringField and SubmitField
from wtforms.validators import DataRequired, Email, EqualTo
from models import db


class LoginForm(FlaskForm):
    email = StringField("email", validators=[DataRequired()])
    password = StringField("name", validators=[DataRequired()])
    submit = SubmitField("Submit")


class AddBikesForm(FlaskForm):
    Brand_name = StringField("Brand Name", validators=[DataRequired()])
    Brand_category = StringField("Brand Category", validators=[DataRequired()])
    M_date = DateField("Manufacture Date", validators=[DataRequired()])
    accessories = StringField("accessories", validators=[DataRequired()])
    image_url = FileField("Image File", validators=[DataRequired()])
    price = FloatField("price", validators=[DataRequired()])
    description = StringField("description", validators=[DataRequired()])
    submit = SubmitField("Submit")

class LoginForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Login")

class RegistrationForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    email = EmailField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    # Uncomment the next line if you want to add a confirm password field
    confirm_password = PasswordField("Confirm Password", validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField("Register")


class OrderForm(FlaskForm):
    submit = SubmitField('Place Order')

