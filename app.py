from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from secret import my_password
from marshmallow import fields, ValidationError, validate
import math


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+mysqlconnector://root:{my_password}@localhost/ecommerce_db'
db = SQLAlchemy(app)
ma = Marshmallow(app)


#create Schemas for customers Accounts products orders
class CustomerSchema(ma.Schema): 
    name = fields.String(required=True)
    email = fields.Email(required=True) 
    phone = fields.String(required=True) 

    class Meta: 
        fields = ("customer_id", "name", "email", "phone")

class AccountSchema(ma.Schema):
    username = fields.String(required=True)
    password = fields.String(required=True) 
    
    class Meta:
        fields = ("account_id", "username", "password","customer_id")
        
class ProductSchema(ma.Schema):
    name = fields.String(required=True, validate=validate.Length(min =1))
    price = fields.Float(required=True, validate=validate.Range(min=0))
    
    class Meta:
        fields = ("product_id", "name", "price")

class OrderSchema(ma.Schema):
    customer_id = fields.Int(required=True)
    order_date = fields.Date(required=True)
    expected_delivery_date = fields.Date(required=True)
    product_id = fields.Int(required=True)  
    quantity = fields.Int(required=True)   

    class Meta:
        fields = ("customer_id", "order_id", "order_date", "expected_delivery_date", "product_id", "quantity")
        
# class OrderItemSchema(ma.Schema):
#     product_id = fields.Int(required=True)
#     quantity = fields.Int(required =True)
    
#     class Meta:
#         fields =("order_item_id", "order_id", "product_id", "quantity")
        
customer_schema = CustomerSchema() 
customers_schema = CustomerSchema(many=True)

account_schema =AccountSchema()
accounts_schema =AccountSchema(many=True)

product_schema =ProductSchema()
products_schema =ProductSchema(many=True)

order_schema =OrderSchema()
orders_schema=OrderSchema(many=True)

# order_item_schema = OrderItemSchema()
# order_items_schema = OrderItemSchema(many=True)
#create tables and columns 
class Customer(db.Model):
    customer_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), nullable=False)
    email = db.Column(db.String(250), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    accounts = db.relationship('CustomerAccount', backref='customer')
    orders = db.relationship('Order', backref='customer')
    
class CustomerAccount(db.Model):
    account_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(250), nullable=False)
    password = db.Column(db.String(250), nullable=False)
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.customer_id'))
    
class Product(db.Model):
    product_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), nullable=False)
    price = db.Column(db.Float, nullable=False)
   
   
   
class Order(db.Model): 

    order_id = db.Column(db.Integer, primary_key=True) 
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.customer_id')) 
    product_id = db.Column(db.Integer, db.ForeignKey('product.product_id'), nullable=False) 
    quantity = db.Column(db.Integer, nullable=False) 
    order_date = db.Column(db.Date, nullable=False) 
    expected_delivery_date = db.Column(db.Date) 
    # customer = db.relationship('Customer', backref='orders') 
    # product = db.relationship('Product', lazy=True)
    
   
    
# class Order(db.Model):
#     customer_id = db.Column(db.Integer, db.ForeignKey('customer.customer_id'))
#     order_date = db.Column(db.Date, nullable=False)
#     expected_delivery_date = db.Column(db.Date)
#     order_id = db.Column(db.Integer, primary_key=True)
#     # quantity =  db.Column(db.Integer, nullable=False)
#     # product_id = db.Column(db.Integer, db.ForeignKey('product.product_id'))
#     order_items = db.relationship('Order', backref='order', lazy="joined")
    
#     quantity = db.Column(db.Integer, nullable=False)
#     product= db.relationship('Product', lazy=True)
    
# class OrderItem(db.Model):#introducting an orderitem so that we can iterate over the class Order
#     order_item_id = db.Column(db.Integer, primary_key=True)
#     order_id = db.Column(db.Integer, db.ForeignKey('order.order_id'),nullable=False)
#     # order_items = db.relationship('OrderItem', backref='order')
#     product_id = db.Column(db.Integer, db.ForeignKey('product.product_id'), nullable=False)
    
# @app.route('/customer', methods=['POST'])
def add_customer():
    try:
        customer_data = customer_schema.load(request.json)
    except ValidationError as err:
        return jsonify(err.messages), 400
    new_customer = Customer(name=customer_data['name'], email=customer_data['email'], phone=customer_data['phone'])
    db.session.add(new_customer)
    db.session.commit()
    return jsonify({"message": "New customer added successfully"}),201

@app.route('/customer/<int:customer_id>', methods=['GET'])
def get_customer(customer_id):
    customer = Customer.query.get_or_404(customer_id)
    return customer_schema.jsonify(customer)

@app.route('/customer/<int:customer_id>', methods=['PUT'])
def update_customer(customer_id):
    customer = Customer.query.get_or_404(customer_id)
    try:
        customer_data = customer_schema.load(request.json)
    except ValidationError as err:
        return jsonify(err.messages), 400
    customer.name = customer_data['name']
    customer.email = customer_data['email']
    customer.phone = customer_data['phone']
    db.session.commit()
    return jsonify({"message": "Customer details updated successfully"}), 200

@app.route('/customer/<int:customer_id>', methods=['DELETE'])
def delete_customer(customer_id):
    customer=Customer.query.get_or_404(customer_id)
    db.session.delete(customer)
    db.session.commit()
    return jsonify({"message": "Customer removed successfully"}),200

@app.route('/customer_account', methods=['POST'])
def add_customer_account():
    try:
        account_data = account_schema.load(request.json)
    except ValidationError as err:
        return jsonify(err.messages),400
    new_account = CustomerAccount(username=account_data['username'], password=account_data['password'],
    customer_id=account_data['customer_id'])
    db.session.add(new_account)
    db.session.commit()
    return jsonify({"message": "New customer account added successfully"})

@app.route('/customer_account/<int:account_id>',methods =['GET'])
def get_customer_account(account_id):
    account = CustomerAccount.query.get_or_404(account_id)
    return account_schema.jsonify(account)

@app.route('/customer_account/<int:account_id>', methods=['PUT'])
def update_customer_account(account_id):
    account =CustomerAccount.query.get_or_404(account_id)
    try:
        account_data = account_schema.load(request.json)
    except ValidationError as err:
        return jsonify(err.messages),400
    account.username = account_data['username']
    account.password = account_data['password']
    db.session.commit()
    return jsonify({"message": "Customer account details updated successfully"}),200

@app.route('/customer_account/<int:account_id>', methods=['DELETE'])
def delete_customer_account(account_id):
    account = CustomerAccount.query.get_or_404(account_id)
    db.session.delete(account)
    db.session.commit()
    return jsonify({"message": "Customer account removed successfully"}),200

@app.route('/product', methods=['POST'])
def add_product():
    try:
        product_data = product_schema.load(request.json)
    except ValidationError as err:
        return jsonify(err.messages),400
    new_product = Product(name=product_data['name'], price= product_data['price'])
    db.session.add(new_product)
    db.session.commit()
    return jsonify({"message": "New product added successfully"}),201

@app.route('/product/<int:product_id>', methods=['GET'])
def get_product(product_id):
    product= Product.query.get_or_404(product_id)
    return product_schema.jsonify(product)

@app.route('/product/<int:product_id>', methods=['PUT'])
def update_product(product_id):
    product = Product.query.get_or_404(product_id)
    try:
        product_data = product_schema.load(request.json)
    except ValidationError as err:
        return jsonify(err.messages),400
    product.name = product_data['name']
    product.price = product_data['price']
    db.session.commit()
    return jsonify({"message": "Product details have been updated successfully"}),200

@app.route('/product/<int:product_id>', methods = ['DELETE'])
def delete_product(product_id):
    product = Product.query.get_or_404(product_id)
    db.session.delete(product)
    db.session.commit()
    return jsonify({"message":"Product removed successfully"}),200

@app.route('/products', methods=['GET'])
def list_products():
    products = Product.query.all()
    return products_schema.jsonify(products)
       
@app.route('/order', methods=['POST'])
def place_order():
    try:
        order_data = order_schema.load(request.json)
    except ValidationError as err:
        return jsonify(err.messages),400
    new_order = Order(
        customer_id=order_data['customer_id'],
        order_date=order_data['order_date'],
        expected_delivery_date=order_data['expected_delivery_date'],
        product_id=order_data['product_id'],
        quantity=order_data['quantity']
    )
    db.session.add(new_order)
    db.session.commit()

    return jsonify({"message":"Order placed successfully"})

@app.route('/order/<int:order_id>', methods=['GET'])
def get_order(order_id):
    order= Order.query.get_or_404(order_id)
    return order_schema.jsonify(order)

@app.route('/order/<int:order_id>/track', methods=['GET'])
def track_order(order_id):
    order =Order.query.get_or_404(order_id)
    return jsonify({"order_date": order.order_date,"expected_delivery_date":order.expected_delivery_date })

@app.route('/customer/<int:customer_id>/orders', methods=['GET'])
def get_order_history(customer_id):
    # customer =Customer.query.get_or_404(customer_id)
    orders = Order.query.filter_by(customer_id=customer_id).all()
    return orders_schema.jsonify(orders)

@app.route('/order/<int:order_id>/total', methods=['GET'])
def calculate_order_total(order_id):
    #using realtionship to calulate the total... item was created 
    order = Order.query.get_or_404(order_id)
    product = Product.query.get_or_404(order.product_id)
    total_price = product.price * order.quantity
    return jsonify({"total_price":total_price}),200
    
    
with app.app_context():
    db.create_all()
    
if __name__ == '__main__':
    app.run(debug=True)