import requests

from controllers.token import Token
from utils.constants import URL_API


class TitleQuery:

    def __init__(self, token: Token):
        self.token = token

    def get_instrument_data(self, instrument_type, country):
        api_key = self.token.get_token()
        headers = {'Authorization': f'Bearer {api_key}'}
        response = requests.get(
            f'{URL_API}/Cotizaciones/{instrument_type}/{country}/Todos?',
            headers=headers)
        return response.json()

    def get_ticker_data(self, mercado, symbol, period):
        api_key = self.token.get_token()
        headers = {'Authorization': f'Bearer {api_key}'}
        response = requests.get(
            f'{URL_API}/{mercado}/Titulos/{symbol}/CotizacionDetalleMobile/{period}',
            headers=headers)
        return response.json()

    def get_historical_series(self, market, symbol, date_from, date_to):
        headers = {'Authorization': f'Bearer {self.token.get_token()}'}
        response = requests.get(
            f'{URL_API}/{market}/Titulos/{symbol}/Cotizacion/seriehistorica/{date_from}/{date_to}/ajustada',
            headers=headers)
        return response.json()
