from flask import Flask, request, jsonify
from flask_cors import CORS
import yfinance as yf

app = Flask(__name__, static_folder='.', static_url_path='')
CORS(app)  # 允許跨來源請求，方便前端在本地端呼叫 API

def get_stock_price(symbol):
    """使用 yfinance 取得指定股票的最新收盤價"""
    try:
        ticker = yf.Ticker(symbol)
        data = ticker.history(period="1d")
        if data.empty:
            return None
        return round(data['Close'].iloc[-1], 2)
    except Exception as e:
        print(f"Error fetching {symbol}: {e}")
        return None

@app.route('/')
def home():
    from flask import send_from_directory
    return send_from_directory('.', 'index.html')

@app.route('/price', methods=['POST'])
def price():
    """接收股票代號清單並回傳即時股價"""
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

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)