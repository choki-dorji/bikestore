from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Bikes(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    Brand_name = db.Column(db.String(100), nullable=False)
    Brand_category = db.Column(db.Text, nullable=False)
    price = db.Column(db.Float, nullable=False)
    M_date = db.Column(db.String(50), nullable=False)
    accessories = db.Column(db.String, nullable=False)
    image_url = db.Column(db.String(200), nullable=False)
    description = db.Column(db.String(200), nullable=False)

class SystemUser(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)

    @property
    def is_active(self):
        return True  # You can implement logic here if needed

    

class Order(db.Model):
    order_id = db.Column(db.Integer, primary_key=True)
    # customer_name = db.Column(db.String(100), nullable=False)
    customer_email = db.Column(db.String(100), nullable=False)
    # user_id = db.Column(db.Integer, nullable=False)
    pname = db.Column(db.String(100), nullable=False)
    pdescription = db.Column(db.Text, nullable=False)
    pprice = db.Column(db.Float, nullable=False)
    pstock_quantity = db.Column(db.Integer, nullable=False)
    pimage_url = db.Column(db.String(200), nullable=False)
    porder_date = db.Column(db.DateTime, nullable=False, default=db.func.current_timestamp())

    product_id = db.Column(db.Integer, db.ForeignKey('bikes.id'), nullable=False)
    
    # Relationship to the Bikes model
    product = db.relationship('Bikes', backref=db.backref('orders', lazy=True))

    
