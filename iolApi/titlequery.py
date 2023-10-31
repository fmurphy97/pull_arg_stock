import requests

from iolApi.token import Token
from iolApi.constants import URL_API, MARKETS, PERIODS, INSTRUMENT_TYPES, COUNTRIES, INSTRUMENT_TYPES_FOR_PANEL


class TitleQuery:

    def __init__(self, token: Token):
        self.token = token

    def get_instrument_data(self, instrument_type, country):
        assert instrument_type in INSTRUMENT_TYPES, f"The instrument type {instrument_type} is not in {INSTRUMENT_TYPES}"
        assert country in COUNTRIES, f"The country {country} is not in {COUNTRIES}"

        api_key = self.token.get_token()
        headers = {'Authorization': f'Bearer {api_key}'}
        response = requests.get(
            f'{URL_API}/Cotizaciones/{instrument_type}/{country}/Todos?',
            headers=headers, verify=False)
        return response.json()

    def get_panel_data(self, instrument_type, panel, country):
        assert instrument_type in INSTRUMENT_TYPES_FOR_PANEL, f"The instrument type {instrument_type} is not in {INSTRUMENT_TYPES_FOR_PANEL}"
        assert country in COUNTRIES, f"The country {country} is not in {COUNTRIES}"
        api_key = self.token.get_token()
        headers = {'Authorization': f'Bearer {api_key}'}
        response = requests.get(
            f'{URL_API}/Cotizaciones/{instrument_type}/{panel}/{country}',
            headers=headers, verify=False)
        return response.json()

    def get_ticker_data(self, market, symbol, period):
        if market not in MARKETS:
            return f"The market {market} is not in {MARKETS}"
        if period not in PERIODS:
            return f"The period {period} is not in {PERIODS}"

        api_key = self.token.get_token()
        headers = {'Authorization': f'Bearer {api_key}'}
        response = requests.get(
            f'{URL_API}/{market}/Titulos/{symbol}/CotizacionDetalleMobile/{period}',
            headers=headers, verify=False)
        return response.json()

    def get_historical_series(self, market, symbol, date_from, date_to):
        assert market in MARKETS, f"The market {market} is not in {MARKETS}"

        headers = {'Authorization': f'Bearer {self.token.get_token()}'}
        response = requests.get(
            f'{URL_API}/{market}/Titulos/{symbol}/Cotizacion/seriehistorica/{date_from}/{date_to}/ajustada',
            headers=headers, verify=False)
        return response.json()
