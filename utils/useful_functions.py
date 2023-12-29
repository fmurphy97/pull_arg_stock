import re

def correct_str(input_str):
    # Correct the columns types
    input_str = input_str.replace(".", "")
    input_str = input_str.replace(",", ".")

    input_str = re.sub("[^0-9^.]", "", input_str)

    if input_str == '':
        input_str = 0.0
    return float(input_str)