# Provides common utility functions used across the application.
# Provides common utility functions used across the application.
import json 

def load_json(path=''):
    """
    This function takes path of json to load it into a variable.

    Args:
        path (str): Path of json to load. Defaults to ''.

    Returns:
        json: Json object will be retuned.
    """
    # Open the JSON file
    with open(path, 'r') as file:
        # Load JSON data from file
        json_obj = json.load(file)
    return json_obj

def write_json(path, data):
    """
    This function takes path of json to write data it into a it.

    Args:
        path (str): Path of json to write. Defaults to ''.

    Returns:
        json: Json object will be retuned.
    """
    # Serialize the dictionary to a JSON formatted string
    json_data = json.dumps(data)
    # Encode the JSON string to bytes
    bytes_data = json_data.encode('utf-8')
    # write json to specified file address.
    with open(path, 'wb') as file:
        file.write(bytes_data)
    return 0