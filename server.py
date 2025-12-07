from flask import Flask, send_from_directory, request, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
import yfinance as yf

app = Flask(__name__, static_folder='.', static_url_path='')
CORS(app)

# PostgreSQL 連線設定
app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://root:8bX1G6w2VLxh5vR04HQaStWlKy7C93ic@hnd1.clusters.zeabur.com:27860/zeabur"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# 股票資料表
class Stock(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(20))
    name = db.Column(db.String(50))
    date = db.Column(db.String(20))
    quantity = db.Column(db.Integer)
    price = db.Column(db.Float)
    receivable = db.Column(db.Float)
    current_price = db.Column(db.Float)

@app.route('/')
def serve_index():
    return send_from_directory('.', 'index.html')

@app.route('/price', methods=['POST'])
def get_price():
    data = request.get_json()
    symbols = data.get('symbols', [])
    prices = {}
    for symbol in symbols:
        try:
            if '.' not in symbol:
                symbol = f"{symbol}.TW"
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period="1d")
            if not hist.empty:
                prices[symbol.split('.')[0]] = round(hist['Close'].iloc[-1], 2)
            else:
                prices[symbol.split('.')[0]] = None
        except Exception as e:
            print(f"Error fetching {symbol}: {e}")
            prices[symbol.split('.')[0]] = None
    return jsonify(prices)

@app.route('/add_stock', methods=['POST'])
def add_stock():
    data = request.get_json()
    stock = Stock(
        code=data.get('code'),
        name=data.get('name'),
        date=data.get('date'),
        quantity=data.get('quantity'),
        price=data.get('price'),
        receivable=data.get('receivable'),
        current_price=data.get('current_price')
    )
    db.session.add(stock)
    db.session.commit()
    return jsonify({'message': 'Stock added successfully'})

@app.route('/get_stocks', methods=['GET'])
def get_stocks():
    stocks = Stock.query.all()
    return jsonify([{
        'id': s.id,
        'code': s.code,
        'name': s.name,
        'date': s.date,
        'quantity': s.quantity,
        'price': s.price,
        'receivable': s.receivable,
        'current_price': s.current_price
    } for s in stocks])

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', port=5000)