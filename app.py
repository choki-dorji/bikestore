# Import necessary modules for Flask, database handling, and form management
import datetime
import os
from flask import Flask, flash, redirect, render_template, request, url_for
from models import Accessories, Order, OrderDetail, db
from forms import AddBikesForm, OrderDetailForm, OrderForm
from models import Bikes
from werkzeug.utils import secure_filename

# Initialize the Flask app
app = Flask(__name__)

# Define base directory and upload folder for image uploads
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'static', 'uploads')

# Flask app configurations: enable CSRF protection, setup SQLite database, and define secret key and upload folder
app.config['WTF_CSRF_ENABLED'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///ecommerce.db'
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Define allowed file extensions for image uploads
ALLOWED_EXTENSION = {'png', 'jpg', 'jpeg'}

# Helper function to check if the uploaded file has an allowed extension
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSION

# Initialize the database with the Flask app
db.init_app(app)

# Function to create database tables when the app is started
def create_tables():
    with app.app_context():
        db.create_all()

# Call function to create tables when the app starts
create_tables()

# Helper function to normalize the category name by making it lowercase
def normalize_category(category):
    normalized = category.lower()
    return normalized

# Helper function to count the total number of items in the cart (i.e., in the `Order` table)
def get_cart_item_count():
    return len(Order.query.all())

# This function makes the cart item count available globally to all templates (using context processor)
@app.context_processor
def inject_cart_count():
    return dict(cart_item_count=get_cart_item_count())

# Route for the homepage, showing all products with a price less than $500
@app.route("/")
def Homepage():
    all_products = Bikes.query.all()
    special_offer_products = [product for product in all_products if product.price < 500]
    return render_template("home.html", products=special_offer_products)

# Route for displaying the products page with optional category and search filters
@app.route("/products", methods=["GET", "POST"])
def Productspage():
    category = request.args.get('category')  # Get category from URL if any
    query = request.args.get('search')  # Get search query from URL if any

    # If a search query is provided, filter products by name, description, or category
    if query:
        products = Bikes.query.filter(
            Bikes.Brand_name.ilike(f"%{query}%") |
            Bikes.description.ilike(f"%{query}%") |
            Bikes.Brand_category.ilike(f"%{query}%")
        ).all()
    # If a category is provided, filter products by the normalized category
    elif category:
        normalized_category = normalize_category(category)
        products = Bikes.query.filter(
            Bikes.Brand_category.ilike(f'%{normalized_category}%') |
            Bikes.Brand_category.ilike(f'%{normalized_category[:-1]}%') |
            Bikes.Brand_category.ilike(f'%{normalized_category}s%') |
            Bikes.Brand_category.ilike(f'%{normalized_category}-bikes%') |
            Bikes.Brand_category.ilike(f'%{normalized_category}-bike%')
        ).all()
    # If no search query or category is provided, show all products
    else:
        products = Bikes.query.all()

    return render_template("products.html", products=products, category=category, query=query)

# Route to view all orders that haven't been purchased (bought = False)
@app.route("/orders")
def all_orders():
    orders = Order.query.filter_by(bought=False).all()

    # If no orders exist, flash a message and redirect to the product page
    if not orders:
        flash("Your cart is empty.", "info")
        return redirect(url_for('Productspage'))

    # Create a list of order details (e.g., product name, price, etc.)
    order_details = []
    for order in orders:
        order_details.append({
            'order_id': order.order_id,
            'product_id': order.product_id,
            'product_name': order.product.Brand_name,
            'product_price': order.product.price,
            'quantity': order.quantity,
            'product_image': order.product.image_url
        })

    # Calculate the total price of all items in the cart
    total_price = sum(order['product_price'] * order['quantity'] for order in order_details)
    return render_template("order.html", order_details=order_details, total_price=total_price)

# Route to update the cart, handling actions like increasing, decreasing, or deleting items
@app.route('/update_cart', methods=['POST'])
def update_cart():
    action = request.form.get('action')  # Get the action (increase, decrease, delete)
    
    if action == 'proceed_to_payment':
        return redirect(url_for('checkout'))

    order_id = int(request.form.get('order_id'))  # Get the order ID

    # Fetch the order by ID and perform the requested action
    order = Order.query.get(order_id)
    if not order:
        flash("Order not found", "error")
        return redirect(url_for('all_orders'))

    # Increase, decrease, or delete the order
    if action == 'increase':
        order.quantity += 1
    elif action == 'decrease':
        if order.quantity > 1:
            order.quantity -= 1
    elif action == 'delete':
        db.session.delete(order)

    # Commit changes to the database
    db.session.commit()

    # Flash a message depending on the action performed
    if action == 'delete':
        flash("Item removed from cart.", "info")
    else:
        flash(f"Quantity updated to {order.quantity}.", "success")

    # Redirect back to the orders page
    return redirect(url_for('all_orders'))

# Route to handle the checkout process, including saving order details to the database
@app.route('/checkout', methods=['GET', 'POST'])
def checkout():
    form = OrderDetailForm()

    # Retrieve all orders that haven't been purchased
    orders = Order.query.all()

    # If no orders exist, flash a message and redirect to the product page
    if not orders:
        flash("No items in your cart.", "warning")
        return redirect(url_for('Productspage'))

    # If the form is submitted and validated, save order details
    if form.validate_on_submit():
        for order in orders:
            new_order_detail = OrderDetail(
                order_id=order.order_id,
                customer_email=form.customer_email.data,
                customer_name=form.customer_name.data,
                shipping_address=form.shipping_address.data,
                postal_code=form.postal_code.data,
                card_number=form.card_number.data,
                cvv=form.cvv.data
            )
            db.session.add(new_order_detail)

        # Mark all orders as bought
        for order in orders:
            order.bought = True

        # Commit all changes to the database
        db.session.commit()

        # Flash a success message and redirect to the homepage
        flash("Order was successfully purchased!", "success")
        return redirect(url_for('Homepage'))

    # If there are form errors, print them and flash an error message
    elif form.errors:
        print(form.errors)
        flash("error", form.errors)

    # Calculate the total price of all orders
    total_price = sum(order.product.price * order.quantity for order in orders)

    # Render the checkout page
    return render_template('checkout.html', orders=orders, total_price=total_price, form=form)

# Route to add a new product, including bike and accessory details, and save them to the database
@app.route("/addproduct", methods=["GET", "POST"])
def addProduct():
    form = AddBikesForm()
    # If the form is submitted and validated
    if form.validate_on_submit():
        # Handle image upload and check if it's valid
        if 'image_url' not in request.files:
            flash("No file part")
            return redirect(request.url)

        file = request.files['image_url']
        if file.filename == '':
            flash("No selected file")
            return redirect(request.url)

        # If the file is valid, save it
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

            # Create a new bike product with the uploaded image
            products = Bikes(
                Brand_name=form.Brand_name.data,
                Brand_category=form.Brand_category.data,
                M_date=form.M_date.data,
                image_url='/static/uploads/' + filename,
                price=form.price.data,
                description=form.description.data
            )

            # Create a new accessory associated with the bike
            new_accessory = Accessories(
                frame=form.frame.data,
                tires=form.tires.data,
                brakes=form.brakes.data,
                weight=form.weight.data,
            )

            # Link the accessory to the bike and save both to the database
            products.accessories.append(new_accessory)
            db.session.add(products)
            db.session.commit()

            # Flash a success message and redirect to the products page
            flash("Product added successfully", "success")
            return redirect(url_for('Productspage'))

        else:
            flash("Invalid file format")
            return redirect(request.url)

    print("form", form.errors)
    return render_template("addProduct.html", form=form)

# Route to log the user out and redirect to the login page
@app.route("/logout")
def logout():
    logout_user()
    flash("You have been logged out.", "info")
    return redirect(url_for('login'))

# Route to place an order for a specific product, adding it to the cart
@app.route('/place_order/<int:product_id>', methods=['GET', 'POST'])
def place_order(product_id):
    form = OrderForm()
    
    # Fetch the product and its associated accessories
    product = Bikes.query.get_or_404(product_id)
    accessories = product.accessories

    # If the form is submitted and validated, create a new order
    if form.validate_on_submit():
        new_order = Order(
            product_id=product_id,
            quantity=1
        )
        db.session.add(new_order)
        db.session.commit()

        # Flash a success message and redirect to the homepage
        flash('Product added to cart!', 'success')
        return redirect(url_for('Homepage'))

    # Render the product details page
    return render_template('productDetails.html', form=form, product=product, accessories=accessories)

# Route to print all orders in the database (for debugging or admin purposes)
@app.route('/print_orders')
def print_orders():
    order_details = OrderDetail.query.all()

    if not order_details:
        return "No orders found."

    # Prepare HTML output for displaying order details
    orders_html = "<h1>Order Details</h1><ul>"
    for order in order_details:
        orders_html += f"<li>Order ID: {order.order_id}<br>"
        orders_html += f"Customer Name: {order.customer_name}<br>"
        orders_html += f"Customer Email: {order.customer_email}<br>"
        orders_html += f"Shipping Address: {order.shipping_address}<br>"
        orders_html += f"Postal Code: {order.postal_code}<br>"
        orders_html += f"Card Number: {order.card_number}<br>"
        orders_html += f"CVV: {order.cvv}</li><br><br>"
    orders_html += "</ul>"

    return orders_html

# Route for the contact page
@app.route("/contact-us")
def contactUs():
    return render_template('contact.html')

# Run the Flask app in debug mode
if __name__ == "__main__":
    app.run(debug=True)
