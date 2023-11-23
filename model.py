import requests
import numpy as np
from sklearn.linear_model import LinearRegression
from datetime import datetime, timezone


def predict_crypto_price(crypto_symbol, target_date, days_of_data=90, currency='usd'):
    def get_historical_data():
        # Define CoinGecko API endpoint
        url = f'https://api.coingecko.com/api/v3/coins/{crypto_symbol}/market_chart'

        # Set the parameters for the request
        params = {
            'vs_currency': currency,
            'days': days_of_data
        }

        # Make the GET request
        response = requests.get(url, params=params)

        # Check if the request was successful
        if response.status_code == 200:
            # Parse the JSON response
            data = response.json()

            # Extract historical price data
            historical_prices = data['prices']

            formatted_historical_data = [(format_timestamp(timestamp), price) for timestamp, price in historical_prices]
            return formatted_historical_data
        else:
            print(f'Error: Failed to retrieve historical data for {crypto_symbol}')
            return None

    def format_timestamp(timestamp):
        date = datetime.fromtimestamp(timestamp / 1000, tz=timezone.utc)
        formatted_date = date.strftime('%Y-%m-%d %H:%M:%S')
        return formatted_date

    def train_linear_regression_model(historical_data):
        timestamps, prices = zip(*historical_data)
        timestamps = np.array([datetime.strptime(ts, '%Y-%m-%d %H:%M:%S').timestamp() for ts in timestamps])
        prices = np.array(prices)

        model = LinearRegression()
        model.fit(timestamps.reshape(-1, 1), prices)

        return model

    def predict_price(model, historical_data, target_date):
        target_timestamp = datetime.strptime(target_date, '%Y-%m-%d').timestamp()
        target_price = model.predict(np.array(target_timestamp).reshape(-1, 1))
        return target_price[0]

    historical_data = get_historical_data()
    if historical_data:
        model = train_linear_regression_model(historical_data)
        predicted_price = predict_price(model, historical_data, target_date)
        return predicted_price
    else:
        return None


# Example usage:
# crypto_name = 'bitcoin'
# target_date = '2023-11-01'  # Specify your desired target date
# predicted_price = predict_crypto_price(crypto_name, target_date)
# if predicted_price is not None:
#     print(f'Predicted price for {crypto_name} on {target_date}: ${predicted_price:.2f}')
# else:
#     print(f'No historical data retrieved for {crypto_name}')
