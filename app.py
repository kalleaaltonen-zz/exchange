from flask import Flask, request, session, jsonify, render_template, redirect, make_response
from models import Side, Order, OrderBook

app = Flask(__name__)
app.secret_key = 'secret key'
app.config['SESSION_TYPE'] = 'filesystem'

trades = []
orderBook = OrderBook(trades)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'name' in request.form:
        session['username'] = request.form['name']
        return redirect('/')
    return render_template('login.html')

@app.route('/logout')
def logout():
    del session['username']
    return redirect('/')

@app.route('/createOrder', methods=['POST'])
def createOrder():
    orderType = Side[request.form['order_type'].upper()]
    price = int(request.form['price'])
    quantity = int(request.form['quantity'])
    order = Order(session['username'], price, quantity, orderType)    
    orderBook.add(order)
    return redirect('/')

@app.route('/orderbook')
def viewOrderbook():
    return render_template('orderbook.html', orderbook=orderBook.getData(), trades=trades)

@app.route('/')
def root():
    if 'username' not in session:
        return redirect('/login')
    return render_template('index.html')