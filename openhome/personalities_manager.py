# import utilities load json function to load json
from openhome.utility import load_json

def load_personality(personality_id):
    """
    This function takes personality id and returns personality object from personalitties json file.

    Args:
        personality_id (string): Personality id to be taken as key of personalities json.

    Returns:
        personality (dictionary): Returns dictionary object from personalities json with corresponding id passed.
    """
    # call load personality function to get personalties json
    personalities_json = load_json('openhome/personalities/personalities.json')
    # check if personality exists
    if not personality_id in personalities_json:
        print('Agent do not exists')
        print('Available list {1:Alan_watts, 2:Ava, 3:Annabele}')
        exit()
    else:
        personality = personalities_json[personality_id]
        with open(personality['personality'], 'r') as file:
            # Read the entire contents of the file into a variable
            personality_content = file.read()
        personality['personality'] = personality_content
    return personality