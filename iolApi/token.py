import requests
import datetime
import pytz

from iolApi.private_constants import USERNAME, PASSWORD
from iolApi.constants import URL_TOKEN, GRANT_TYPE
from iolApi.date_parser import str_to_date


class Token:

    def __init__(self):

        self._access_token = None
        self.token_type = None
        self.refresh_token = None
        self.expiry_date = None
        self.refresh_expiry_date = None

        self.new_access_token()

    def get_token(self):
        now = datetime.datetime.now(pytz.UTC)

        if now >= self.expiry_date:
            if now < self.refresh_expiry_date:
                self.refresh_token()
            else:
                self.new_access_token()

        return self._access_token

    def new_access_token(self):
        # Set the header parameters
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Host': 'api.invertironline.com'
        }

        # Set the body parameters
        data = {
            'username': USERNAME,
            'password': PASSWORD,
            'grant_type': GRANT_TYPE
        }

        # Make a POST request
        response = requests.post(URL_TOKEN, headers=headers, data=data)

        response_json = response.json()

        self._access_token = response_json['access_token']
        self.token_type = response_json['token_type']
        self.refresh_token = response_json['refresh_token']
        self.expiry_date = str_to_date(response_json['.expires'])
        self.refresh_expiry_date = str_to_date(response_json['.refreshexpires'])

    def refresh_token(self):
        # set new access token and refresh token using the refresh token
        # TODO: update this to really refresh the token instead of making a new one
        self.new_access_token()
