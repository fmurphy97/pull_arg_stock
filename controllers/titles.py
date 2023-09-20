import requests

from controllers.token import Token
from utils.constants import URL_API


class Titles:

    def __init__(self, token: Token):
        self.token = token

    def get_titles(self):
        headers = {'Authorization': f'Bearer {self.token.get_token()}'}
        response = requests.get(f'{URL_API}/Titulos/FCI', headers=headers)
        return response.json()

    def get_quotes(self, country):
        headers = {'Authorization': f'Bearer {self.token.get_token()}'}
        response = requests.get(
            f'{URL_API}/{country}/Titulos/Cotizacion/Instrumentos', headers=headers)
        return response.json()

    def get_historical_series(self, market, symbol, date_from, date_to):
        headers = {'Authorization': f'Bearer {self.token.get_token()}'}
        response = requests.get(
            f'{URL_API}/{market}/Titulos/{symbol}/Cotizacion/seriehistorica/{date_from}/{date_to}/ajustada',
            headers=headers)
        return response.json()
