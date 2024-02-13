import requests
from openhome.utility import write_json
import json 
import openhome.app_globals

def mood_detector(message):
    """This function takes message send it to emotion detector api to get emotions dictionaty.

    Args:
        message (str): user message.

    Returns:
        mood_dict (dict): Returns mode dictionary with key as emotion class and value as score for corresponding emotion class.
    """
    url = "https://api.apilayer.com/text_to_emotion"
    payload = message.encode("utf-8")
    headers= {
    "apikey": "x3YITfG9mhU8AyvP2FtOAP1eiGeHhGT5"
    }

    response = requests.request("POST", url, headers=headers, data=payload)

    status_code = response.status_code
    mood_dict = {
        "Angry": 0,
        "Fear": 0,
        "Happy": 0,
        "Sad": 0,
        "Surprise": 0
        }

    if status_code == 200:
        mood_dict = json.loads(response.text)
    else:
        print(response)
    return mood_dict

def average_dict_values(current_mood_dict, mood_json):
    """This function takes to dictionaries with same keys to average them.

    Args:
        current_mood_dict (dict): Current mood returned from mood_detector function.
        mood_json (dict): Mood dictionary from mood.json/averaged mood dictioanry

    Returns:
        averaged_dict (dict): Average mood dictionary to be stored in mood.json
    """
    # Step  1: Initialize an empty dictionary
    averaged_dict = {}
    
    # Step  2: Iterate through the keys in both dictionaries
    for key in set(current_mood_dict.keys()).union(mood_json.keys()):
        # Step  3 &  4: Calculate the average if the key exists in both dictionaries
        if key in current_mood_dict and key in mood_json:
            averaged_dict[key] = (current_mood_dict[key] + mood_json[key]) /  2
            
    # Step  5: Return the new dictionary
    return averaged_dict

def sort_dictionary(average_mood_dict):
    """
    This function takes a dictinary and returned its descending order sorted version.

    Args:
        average_mood_dict (dict): Dictionary to be sorted in descending order

    Returns:
        sorted_dict (dict): Sorted dictionary.
    """
    # Sort dictionary by value in descending order
    sorted_dict = sorted(average_mood_dict.items(), key=lambda x: x[1], reverse=True)
    # Convert the sorted list of tuples 
    # back into a dictionary
    sorted_dict = dict(sorted_dict)
    # return the sorted dictionary.
    return sorted_dict
    
def mood_evolver(user_latest_message, mood_json, instructions):
    """
    This is the escence model of this module. taht call all other functions to create a customizable prompt.

    Args:
        user_latest_message (str): Latest user message.
        mood_json (dict): It is a dictioanry from mood.json or averaged json.
        instructions (str): Instruction string from mood evolving instruction text file.

    Returns:
        prompt (str): Customized prompt only for mood.
        average_mood_dict (dict): DIctioanry to be passed in next iteration to forbide file reading again and again.
    """
    current_mood_dict = mood_detector(user_latest_message)
    print('current mode scores', current_mood_dict)
    average_mood_dict = average_dict_values(current_mood_dict, mood_json)

    # print(average_mood_dict)
    # sort the mood json to get heighest score in first place
    sorted_average_mood_dict = sort_dictionary(average_mood_dict)
    # store average mood dictonary to our json
    write_json(path='personalities/mood.json', data=sorted_average_mood_dict)
     # store current mood dictonary to our json
    write_json(path='personalities/current_mood.json', data=current_mood_dict)
    # prepare prompt
    # get keys of sorted average dictionary into list to get them by index.
    moods_values = list(sorted_average_mood_dict.keys())
    # get emotion with heighest score.
    max_score_class = moods_values[0]
    # get emotion with second heighest score.
    second_max_score_class = moods_values[1]
    # get emotion with third heighest score.
    third_max_score_class = moods_values[2]
    prompt = instructions.format(max_score_class = max_score_class, 
                                second_max_score_class = second_max_score_class,
                                third_max_score_class = third_max_score_class )
    return prompt, average_mood_dict

def get_customized_prompt(mood_prompt, initial_prompt):
    """
    This function takes two prompts and join them as one single prompt to be passed to chatgpt function.

    Args:
        mood_prompt (str): Customized mood propmt generated through mood eveloer funtion.
        initial_prompt (str): Initial personality propmt

    Returns:
        prompt: prompt to begiven to chatgpt, combination of customized mood prompt and initla prompt.
    """
    prompt = mood_prompt + " " + initial_prompt
    # set the global variable to Flase to end the loading sound.
    app_globals.play_loading_sound_global = False
    return prompt
