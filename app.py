import datetime
import os
from flask import Flask, flash, redirect, render_template, request, session, url_for
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from models import Order, SystemUser, db
from forms import AddBikesForm, LoginForm, OrderForm, RegistrationForm
from models import Bikes
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash




app = Flask(__name__)

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'static', 'uploads')

app.config['WTF_CSRF_ENABLED'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///ecommerce.db'
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# allowed files extension
ALLOWED_EXTENSION = {'png','jpg','jpeg'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.',1)[1].lower() in ALLOWED_EXTENSION


db.init_app(app)


def create_tables():
    with app.app_context():
        db.create_all()

create_tables()

login_manager = LoginManager(app)
login_manager.login_view = 'login'

def normalize_category(category):
    # Remove common variations and lower the case
    normalized = category.lower()
    return normalized

@login_manager.user_loader
def load_user(user_id):
    return SystemUser.query.get(int(user_id))

def get_cart_item_count():
    return len(Order.query.all())

# @login_required
@app.route("/")
def Homepage():
    all_products = Bikes.query.all()
    
    # Define a special offer filter the bikrs whose price are below 500 doolar
    special_offer_products = [product for product in all_products if product.price < 500] 

    return render_template("home.html", products=special_offer_products)


# @login_required
@app.route("/products", methods=["GET", "POST"])
def Productspage():
    category = request.args.get('category')
    query = request.args.get('search')  # Get the search query from the request
    
    if query:
        # Search for products where name, description, or category matches the query
        products = Bikes.query.filter(
            Bikes.Brand_name.ilike(f"%{query}%") | 
            Bikes.description.ilike(f"%{query}%") |
            Bikes.Brand_category.ilike(f"%{query}%")
        ).all()
    elif category:
        # If there's no search query but a category is selected, filter by category
        normalized_category = normalize_category(category)
        products = Bikes.query.filter(
            Bikes.Brand_category.ilike(f'%{normalized_category}%') |
            Bikes.Brand_category.ilike(f'%{normalized_category[:-1]}%') |  # Check singular form
            Bikes.Brand_category.ilike(f'%{normalized_category}s%') |  # Check plural form
            Bikes.Brand_category.ilike(f'%{normalized_category}-bikes%') |  # Check E-bikes specifically
            Bikes.Brand_category.ilike(f'%{normalized_category}-bike%')  # Check E-bike specifically
        ).all()
    else:
        # If no search query or category, show all products
        products = Bikes.query.all()

    return render_template("products.html", products=products, category=category, query=query)


@app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = SystemUser.query.filter_by(username=form.username.data).first()
        if user and check_password_hash(user.password, form.password.data):
            login_user(user)
            flash("Login successful!", "success")
            return redirect(url_for('Homepage'))
        else:
            flash("Login failed. Check your username and password.", "danger")
    return render_template("login.html", form=form)

@app.route("/register", methods=["GET", "POST"])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = generate_password_hash(form.password.data, method='scrypt')
        new_user = SystemUser(
            username=form.username.data,
            email=form.email.data,
            password=hashed_password
        )
        db.session.add(new_user)
        db.session.commit()
        # Process the registration (e.g., save user to database)
        flash("Registration successful!", "success")
        return redirect(url_for('login'))  # Redirect to login or another page
    return render_template("register.html", form=form)

@app.route("/orders")
def all_orders():
    orders = Order.query.all()
    print("length", len(orders))
    
    # You can create a list of order details including product info
    order_details = []
    for order in orders:
        order_details.append({
            'order_id': order.order_id,
            'product_id': order.product_id,
            'product_name': order.product.Brand_name,  # Accessing product details
            'product_price': order.product.price,
            'quantity':order.quantity,
            'product_image': order.product.image_url
            # Add any other product details you want
        })
    
    total_price = sum(order['product_price'] * order['quantity'] for order in order_details)
    return render_template("order.html", order_details=order_details, total_price=total_price)

@app.route('/update_cart', methods=['POST'])
def update_cart():
    action = request.form.get('action')

    if action == 'proceed_to_payment':
        return redirect(url_for('checkout'))

    order_id = int(request.form.get('order_id'))

    # Get the order by its ID
    order = Order.query.get(order_id)
    if not order:
        flash("Order not found", "error")
        return redirect(url_for('all_orders'))

    # Handle different actions (increase, decrease, delete)
    if action == 'increase':
        order.quantity += 1
    elif action == 'decrease':
        if order.quantity > 1:  # Don't allow the quantity to drop below 1
            order.quantity -= 1
    elif action == 'delete':
        db.session.delete(order)
    
    # Commit the changes
    db.session.commit()

    # Flash message based on action
    if action == 'delete':
        flash("Item removed from cart.", "info")
    else:
        flash(f"Quantity updated to {order.quantity}.", "success")

    # Redirect back to the cart page
    return redirect(url_for('all_orders'))

@app.route('/checkout', methods=['GET', 'POST'])
def checkout():    
    # Retrieve all orders for the current user
    orders = Order.query.all()  # Assuming you're storing all orders in the `Order` model

    # Calculate the total price
    total_price = sum(order.product.price * order.quantity for order in orders)

    # Render the checkout template and pass the total price
    return render_template('checkout.html', orders=orders, total_price=total_price)




@app.route("/addproduct", methods=["GET", "POST"])
def addProduct():
    form = AddBikesForm()
    if form.validate_on_submit():
        # Check if the file part is present in the request
        if 'image_url' not in request.files:
            flash("No file part")
            return redirect(request.url)
        
        file = request.files['image_url']

        # If no file is selected
        if file.filename == '':
            flash("No selected file")
            return redirect(request.url)
        
        # Save the file if it's allowed
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

            # Create the bike instance with the uploaded filename
            products = Bikes(
                Brand_name=form.Brand_name.data, 
                Brand_category=form.Brand_category.data, 
                M_date=form.M_date.data,
                accessories=form.accessories.data,
                image_url='/static/uploads/' + filename,  # Save the path of the image
                price=form.price.data,
                description=form.description.data
            )
            
            # Add the new bike to the database
            db.session.add(products)
            db.session.commit()
            flash("Product added successfully")
            return redirect(url_for('Productspage'))  # Redirect to products page after successful addition
        else:
            flash("Invalid file format")
            return redirect(request.url)
    return render_template("addProduct.html", form=form)

@login_required
@app.route("/logout")
def logout():
    logout_user()
    flash("You have been logged out.", "info")
    return redirect(url_for('login'))


@app.route('/place_order/<int:product_id>', methods=['GET', 'POST'])
def place_order(product_id):
    form = OrderForm()
    # Fetch the product details
    product = Bikes.query.get_or_404(product_id)
    if form.validate_on_submit():        
          # Mark the session as modified
        new_order = Order(
        product_id=product_id, # Using the product ID from the URL
            quantity=1
        )
        db.session.add(new_order)
        db.session.commit()
        flash('Product added to cart!', 'success')
       
        return redirect(url_for('Homepage'))
    return render_template('productDetails.html', form=form, product=product)



@app.route("/abcd")
def done():
    orders = OrderDetail.query.all()
    print("orders", orders)
    return orders


if __name__ == "__main__":  
    app.run(debug=True)