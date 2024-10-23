from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# Junction table for many-to-many relationship
bike_accessory_association = db.Table('bike_accessory_association',
    db.Column('bike_id', db.Integer, db.ForeignKey('bikes.id'), primary_key=True),
    db.Column('accessory_id', db.Integer, db.ForeignKey('accessories.id'), primary_key=True)
)

class Bikes(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    Brand_name = db.Column(db.String(100), nullable=False)
    Brand_category = db.Column(db.Text, nullable=False)
    price = db.Column(db.Float, nullable=False)
    M_date = db.Column(db.String(50), nullable=False)
    image_url = db.Column(db.String(200), nullable=False)
    description = db.Column(db.String(200), nullable=False)

    accessories = db.relationship('Accessories', secondary=bike_accessory_association, backref='bikes')  # Many-to-many relationship
class Accessories(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    frame = db.Column(db.String(100), nullable=False)
    tires = db.Column(db.String(100), nullable=False)
    brakes = db.Column(db.String(100), nullable=False)
    weight = db.Column(db.Float, nullable=False)

class Order(db.Model):
    order_id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('bikes.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    bought = db.Column(db.Boolean, default=False)
    product = db.relationship('Bikes', backref=db.backref('orders', lazy=True))

class OrderDetail(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('order.order_id'), nullable=False)
    customer_email = db.Column(db.String(150), nullable=False)
    customer_name = db.Column(db.String(150), nullable=False)
    shipping_address = db.Column(db.String(150), nullable=False)
    postal_code = db.Column(db.String(10), nullable=False)
    card_number = db.Column(db.String(16), nullable=False)
    cvv = db.Column(db.String(4), nullable=False)
    # relation ship to orders table
    order = db.relationship('Order', backref='order_details', lazy=True)
