import datetime




def str_to_date(date_str):
    date_format = '%a, %d %b %Y %H:%M:%S %Z'
    parsed_date = datetime.datetime.strptime(date_str, date_format)
    return parsed_date

