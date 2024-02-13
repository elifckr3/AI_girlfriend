# Processes history.json to extract trends and relevant information.
import json

# Load existing history
with open('history.json', 'r') as file:
    history = json.load(file)