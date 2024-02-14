import re
from openhome.utility import load_json
def main(message, personality, resume_event):
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
            personality = peronalities_json[personality_id]
            feedback = personality['greetings']
        else:
            # get names of all personalities available
            peronalities_name = [peronalities_json[person_id].get('name').replace('_', ' ') for person_id in peronalities_json]
            regex_pattern = "|".join(peronalities_name)  # Creates a pattern like 'ava|alan watts|annabele'
            personality_name = re.findall(regex_pattern, message)
            if peronalities_name:
                # get the name and if it contains space join it with under score and strip leading and trailing spaces.
                personality_name = personality_name[0].replace(' ', '_').strip()
                for id in peronalities_json:
                    if peronalities_json[id]['name'] == peronalities_name:
                        personality_id = id
                        break
                personality = peronalities_json[personality_id]
                feedback = personality['greetings']
        # finally check if we hae got personality or not
        if personality is None:
            feedback = "The personality you provided is not in existing ones, please choose a valid option from 1,2 and 3."
        return {
            "feedback": feedback,
            "result":personality
        }
    except Exception as e:
        print(e)
        feedback = "Exception occurs %s" %e
        return {
            "feedback": feedback,
            "result":personality
        }
