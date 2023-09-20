import datetime
import pytz

from utils.private_constants import TIMEZONE


def str_to_date(date_str):
    date_format = '%a, %d %b %Y %H:%M:%S %Z'
    parsed_date = datetime.datetime.strptime(date_str, date_format)

    # Assign the Buenos Aires timezone to the datetime object
    parsed_date = pytz.timezone(TIMEZONE).localize(parsed_date)
    return parsed_date
