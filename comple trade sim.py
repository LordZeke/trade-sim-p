import random
import requests
from flask import Flask, request, render_template, jsonify
from flask_sqlalchemy import SQLAlchemy

# Initialize Flask app and database
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///simulator.db'
db = SQLAlchemy(app)

# Database model for User
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    cash = db.Column(db.Float, nullable=False)
    portfolio = db.Column(db.PickleType, nullable=False)

db.create_all()

# Trade Simulator class
class TradeSimulator:
    def __init__(self):
        self.portfolio = {}
        self.cash = 10000  # Fake money
        self.stock_data = self.fetch_stock_data()

    def fetch_stock_data(self):
        # Mock stock data (for real application, use live API)
        stocks = ['AAPL', 'GOOGL', 'MSFT', 'AMZN', 'TSLA']
        data = {stock: random.uniform(100, 1500) for stock in stocks}
        return data

    def display_stock_prices(self):
        print("Current Stock Prices:")
        for stock, price in self.stock_data.items():
            print(f"{stock}: ${price:.2f}")

    def buy_stock(self, stock, amount):
        if stock not in self.stock_data:
            print(f"Stock {stock} not available.")
            return False
        price = self.stock_data[stock]
        total_cost = price * amount
        if total_cost > self.cash:
            print("Not enough cash.")
            return False
        self.cash -= total_cost
        if stock in self.portfolio:
            self.portfolio[stock] += amount
        else:
            self.portfolio[stock] = amount
        print(f"Bought {amount} shares of {stock} at ${price:.2f} each.")
        return True

    def sell_stock(self, stock, amount):
        if stock not in self.portfolio or self.portfolio[stock] < amount:
            print("Not enough shares to sell.")
            return False
        price = self.stock_data[stock]
        total_revenue = price * amount
        self.cash += total_revenue
        self.portfolio[stock] -= amount
        if self.portfolio[stock] == 0:
            del self.portfolio[stock]
        print(f"Sold {amount} shares of {stock} at ${price:.2f} each.")
        return True

    def show_portfolio(self):
        print("\nYour Portfolio:")
        for stock, amount in self.portfolio.items():
            print(f"{stock}: {amount} shares")
        print(f"Cash available: ${self.cash:.2f}")

# Stock data fetcher class
class StockDataFetcher:
    API_KEY = 'YOUR_ALPHAVANTAGE_API_KEY'
    
    @staticmethod
    def get_stock_price(symbol):
        url = 'https://www.alphavantage.co/query'
        params = {
            'function': 'TIME_SERIES_INTRADAY',
            'symbol': symbol,
            'interval': '1min',
            'apikey': StockDataFetcher.API_KEY
        }
        response = requests.get(url, params=params)
        data = response.json()
        if 'Time Series (1min)' in data:
            latest_data = list(data['Time Series (1min)'].values())[0]
            return float(latest_data['1. open'])
        else:
            return None

# Flask routes
@app.route('/')
def index():
    stock_symbols = ['AAPL', 'GOOGL', 'MSFT', 'AMZN', 'TSLA']
    stock_data = {symbol: StockDataFetcher.get_stock_price(symbol) for symbol in stock_symbols}
    return render_template('index.html', stock_data=stock_data, cash=simulator.cash, portfolio=simulator.portfolio)

@app.route('/buy', methods=['POST'])
def buy():
    stock = request.form['stock'].upper()
    amount = int(request.form['amount'])
    success = simulator.buy_stock(stock, amount)
    return jsonify({'message': 'Purchase completed' if success else 'Failed to purchase', 'cash': simulator.cash, 'portfolio': simulator.portfolio})

@app.route('/sell', methods=['POST'])
def sell():
    stock = request.form['stock'].upper()
    amount = int(request.form['amount'])
    success = simulator.sell_stock(stock, amount)
    return jsonify({'message': 'Sale completed' if success else 'Failed to sell', 'cash': simulator.cash, 'portfolio': simulator.portfolio})

if __name__ == "__main__":
    simulator = TradeSimulator()  # Initialize the simulator
    app.run(debug=True)
