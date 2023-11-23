import requests
from flask import redirect, render_template, session
from functools import wraps


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function


def apology(message, code=400):
    def escape(s):
        for old, new in [("-", "--"), (" ", "  "), ("_", "__"), ("?", "~q"),
                         ("%", "~p"), ("#", "~h"), ("/", "~s"), ("\"", "''")]:
            s = s.replace(old, new)
        return s
    return render_template("apology.html", top=code, bottom=escape(message)), code


def lookup(symbol):
    try:
        # CoinGecko API endpoint for cryptocurrency data
        url = f"https://api.coingecko.com/api/v3/simple/price?ids={symbol}&vs_currencies=usd"

        # Query the CoinGecko API
        response = requests.get(url)
        response.raise_for_status()

        # Check if the response contains data
        data = response.json()
        if symbol in data and 'usd' in data[symbol]:
            price = data[symbol]['usd']
            return {
                "name": symbol,
                "price": price,
                "symbol": symbol
            }
        else:
            print(f"API response does not contain data for {symbol}.")
            return None

    except requests.exceptions.RequestException as e:
        print(f"Request Error: {e}")
        return None
    except ValueError as e:
        print(f"Value Error: {e}")
        return None
    except KeyError as e:
        print(f"Key Error: {e}")
        return None


def get_symbol_by_name(name):
    try:
        # CoinGecko API endpoint to search for a cryptocurrency by name
        url = f"https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&ids={name}&order=market_cap_desc&per_page=1&page=1&sparkline=false"

        # Query the CoinGecko API
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()

        if data:
            # Extract the symbol from the response
            symbol = data[0]['symbol']
            return symbol

    except (requests.RequestException, ValueError, KeyError, IndexError):
        return None
        

def usd(value):
    return f"${value:,.2f}"