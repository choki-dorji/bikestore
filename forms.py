from datetime import date  # Correct import
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm  # Import FlaskForm
from wtforms import EmailField, PasswordField, SelectField, StringField, SubmitField, IntegerField, DateField, FloatField, FileField, TextAreaField, ValidationError # Import StringField and SubmitField
from wtforms.validators import DataRequired, Email, EqualTo, Length, NumberRange
from models import db


class AddBikesForm(FlaskForm):
    # brand name of the bicycle
    Brand_name = StringField("Brand Name", validators=[DataRequired()])
    # cateory of the bicycle as for this system it is restricted tto one listed below
    Brand_category = SelectField("Brand Category", choices=[
        ('Mountain Bike'),
        ('E-Bikes'),
        ('Gravel Bike'),
        ('Folding Bike'),
        ('Fixed Gear Bike'),
        ('Touring Bike')
    ],
     validators=[DataRequired()])
#    Manufactre date so that buyer can check the model in which year it was manufactured
    M_date = DateField("Manufacture Date", validators=[DataRequired()])
    # image so that buyer can view the datail image of the bicycle
    image_url = FileField("Image File", validators=[DataRequired()])
    # Total price of the bicycle
    price = FloatField("price", validators=[DataRequired(), NumberRange(min=0.01, message="Price must be a positive value")])
    # description of the bicycle
    description = StringField("description", validators=[DataRequired()])

# frame means material and size of the bicycle
    frame = SelectField('Frame', choices=[
        ('carbon_54', 'Carbon fiber, 54cm'),
        ('aluminum_56', 'Aluminum, 56cm'),
        ('steel_58', 'Steel, 58cm'),
        ('titanium_60', 'Titanium, 60cm'),
    ], validators=[DataRequired()])


# tires means the types of tyres, which may depend on size, tire type and pattern on the tire
    tyres = [('700x25c Road Slick Tires'),('29x2.4 Mountain Knobby Tubeless Tires'),('26x2.1 Hybrid Semi-Slick Tires'),('700x40c Gravel Tires'), ('29x2.2 Trail Tubeless Tires')]
    tires = SelectField('Tires', choices=tyres, validators=[DataRequired()])
    # means to the system that propels the bike, including the chain, gears, pedals, crankset, and derailleurs.
    # Means to the type of braking system used on the bike, 
    # such as disc brakes, rim brakes, or hydraulic brakes.
    brakes = SelectField('Brakes', choices=[('disc brakes'),('rim brakes'),('hydraulic brakes')], validators=[DataRequired()])
    # weight of the bicycle
    weight = FloatField('Weight (kg)', validators=[DataRequired(), NumberRange(min=0)])

    def validate_M_date(form, field):
        if field.data > date.today():
            raise ValidationError("Manufacture date cannot be in the future. Please select today or a past date.")

    submit = SubmitField("Submit")



class OrderForm(FlaskForm):
    submit = SubmitField('Place Order')

class OrderDetailForm(FlaskForm):
    # email of the customer who wamts to purchase bicycle
    customer_email = EmailField('Customer Email', validators=[DataRequired(), Email()])
    # name of the customer who wamts to purchase bicycle
    customer_name = StringField('Customer Name', validators=[DataRequired()])

    # address of the customaer in which he or she wants to location the poducts want to be delivered
    shipping_address = StringField('Shipping Address', validators=[DataRequired()])
    
    # his or hers postal code for the location
    postal_code = StringField('Postal Code', validators=[DataRequired(), Length(max=10)])
    
    # his or her card number
    card_number = StringField('Card Number', validators=[DataRequired(), Length(min=16, max=16)])
    
    # card vefrification valiue(shoild be 4 digit)
    cvv = StringField('CVV', validators=[DataRequired(), Length(min=3, max=4)])
    submit = SubmitField('Submit Order Details')
