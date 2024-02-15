import re
from openhome.utility import load_json
from fuzzywuzzy import process
import sys
import traceback
def main(message, personality, resume_event):
    """
    This function takes user message with switch personality command current personality nd resme event arguments and return
    updated personality.

    Args:
        message (str): muser text message for switching persoanlity.
        personality (dict): personality idct object.
        resume_event (bool): resume_event is not use in this function but for dynamic syyncronization of calls to all main functions of 
        capabilities modules in capabilities manger capabilites for loop.

    Returns:
        dict: A dictionary with the following keys:
            'feedback': message to be play using text to speech module..
            'result': personality object(dict) if found else NOne.
    """
    # replce number in case if they are in letters
    message = message.replace("one", "1").replace("two", "2").replace("three", "3").replace('four', "4")
    message = message.replace('five',"5").replace('six',"6").replace('seven',"7").replace('eight',"8")
    message = message.replace('nine',"9").replace('ten',"10")
    # initialize personality to noe
    personality = None
    try:
        # load personalities json
        peronalities_json = load_json(path='openhome/personalities/personalities.json')

        # check if user said a personality number or not
        personality_id = re.findall(r'\d+', message)
        if personality_id:
            personality_id = personality_id[0]
            if personality_id in peronalities_json:
                personality = peronalities_json[personality_id]
                feedback = personality['greetings']
        else:
            message = message.lower()
            # get names of all personalities available
            personality_names = [peronalities_json[person_id]['name'].replace('_', ' ').lower() for person_id in peronalities_json]
            # get the name and if it contains space join it with under score and strip leading and trailing spaces.
            # Use process.extractOne to find the best match
            best_match = process.extractOne(message, personality_names)
            print('best match of personality: ',best_match)
            # Check if the best match has a high enough score to consider it a match
            # Adjust the threshold as needed (default is  80)
            if best_match and best_match[1] >=  60:
                for person_id in peronalities_json:
                    if best_match[0].replace(' ', "_") == peronalities_json[person_id]['name']:
                        personality_id = person_id
                        # print(personality_id)
                        # get the personality dict from its id
                        personality = peronalities_json[personality_id]
                        feedback = personality['greetings']
                        break
            
        # finally check if we hae got personality or not
        if personality is None:
            personality_names = [peronalities_json[person_id]['name'].replace('_', ' ').lower() + " " for person_id in peronalities_json]
            total_available_personalities = len(personality_names)
            personality_names = personality_names[0:5]
            available_personalities = ""
            for personality_name in personality_names:
                available_personalities += personality_name + " "
            feedback = "The personality you provided is not in existing ones, please choose a valid option, some of available personalities are %s or you can provide a number from 1,2,3 so on till %s"%(available_personalities,total_available_personalities)
        return {
            "feedback": feedback,
            "result":personality
        }
    except Exception as e:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        traceback_details = {
            'filename': exc_traceback.tb_frame.f_code.co_filename,
            'lineno': exc_traceback.tb_lineno,
            'name': exc_traceback.tb_frame.f_code.co_name,
            'type': exc_type.__name__,
            'message': str(exc_value)
        }
        print(f"An error of type {traceback_details['type']} occurred on line "
            f"{traceback_details['lineno']} in {traceback_details['filename']}. "
            f"Error message: {traceback_details['message']}")
        feedback = "Exception occurs %s" %e
        return {
            "feedback": feedback,
            "result":personality
        }
