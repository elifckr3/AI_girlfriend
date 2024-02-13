from pydub import AudioSegment
from pydub.playback import play
import os
import random
from time import sleep
# import global variable for playing loading sound
import openhome.app_globals

def play_loading_sound(directory_path):
    """
    This function plays the loading sound, ramdomly, until chatgpt response.

    Args:
        path (str): audio file path to paly.
    """
    while openhome.app_globals.play_loading_sound_global:
        sleep(openhome.app_globals.sleep)
        file_full_path = get_random_file(directory_path)
        audio = AudioSegment.from_mp3(file_full_path)
        play(audio)
        



def get_random_file(directory_path):
    """
    Returns a random filename, chosen among the files of the given directory path.
    """
    files = os.listdir(directory_path)
    if files:  # Check if the directory is not empty
        random_file =  random.choice(files)
        full_path = os.path.join(directory_path, random_file)
        return full_path
    else:
        print('Directory is empty.')
        return None  # Or handle the case where the directory is empty