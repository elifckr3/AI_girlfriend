import json 
import spotipy 
from spotipy.oauth2 import SpotifyClientCredentials
from time import sleep
import subprocess
import random
import sys
import platform

# Function to get a random track from a playlist
def get_random_track(spotifyObject):
    try:
        # Retrieve the user's playlists
        playlists = spotifyObject.current_user_playlists()
        play_list = playlists['items'][0]['id']
        # print(play_list)
        playlist_tracks = spotifyObject.playlist_tracks(play_list)
        total_tracks = playlist_tracks['total']
        # Generate a random number between  0 and number of total_tracks 
        random_number = random.randint(0,  total_tracks)
        random_track = playlist_tracks['items'][random_number]['track']['id']
    except Exception as e:
        # print(e)
        random_track = '69uxyAqqPIsUyTO8txoP2M'
    return random_track

# Used to Play song on spotify
def play_song(search_song=''):
    if platform.system() == 'Linux':
        try:
            # Command to open Spotify installed via Snap on Ubuntu
            subprocess.Popen(['spotify'])

            chat_response = "Music is playing, from one of your playlist what's next"
        except FileNotFoundError:
            # If Spotify is not found, install it
            if install_spotify():
                print("Spotify has been installed successfully. Please restart your script.")
                subprocess.Popen(['spotify'])
                chat_response = "Login to spotify and play music again."
            else:
                print("Failed to install Spotify.")
            sleep(2)
    # for mac check ~/Applications/Spotify.app

    client_id = "9444715f35444b75af750ac3824eadb0"
    client_secret = "4782fc3b943e4605945d96a4ab54d2a2"
    redirect_uri = 'http://127.0.0.1:8080/'

    # Define the required scopes
    scope = ['app-remote-control', 'user-read-playback-state', 'user-modify-playback-state']

    # Create a SpotifyOAuth object
    sp_oauth = spotipy.SpotifyOAuth(client_id=client_id, client_secret=client_secret, redirect_uri=redirect_uri, scope=scope)

    # Create a Spotify client with the OAuth manager
    spotifyObject = spotipy.Spotify(auth_manager=sp_oauth)
    if search_song:
        results = spotifyObject.search(search_song, 1, 0, "track") 
        songs_dict = results['tracks'] 
        song_items = songs_dict['items'] 
        song = song_items[0]['external_urls']['spotify'] 
        track_id = song.split('/')[-1]
    else:
        track_id = get_random_track(spotifyObject)
    # print(track_id)
    devices = spotifyObject.devices()
    # print(devices)
    device_id = None
    data = {}
    # Start playback on the active device
    if devices['devices']: 
        device_id = devices['devices'][0]['id']  # Set this to your device's ID if you have a specific device you want to play on
    try:
        # Your code to start playback
        spotifyObject.start_playback(device_id=device_id, context_uri=None, uris=["spotify:track:"+track_id], offset=None)
    except spotipy.exceptions.SpotifyException as e:
        print(e)
    return

# Used to Install Spotify app
def install_spotify():
    "Installing spotify, PLease wait..."
    # Determine the OS and install Spotify accordingly
    if platform.system() == 'Linux':
        # For Linux systems, use snap to install Spotify
        subprocess.call(['sudo', 'apt', 'update'])
        subprocess.call(['sudo', 'snap', 'install', 'spotify'])
    elif platform.system() == 'Windows':
        # For Windows systems, download the installer from Spotify's website
        # This requires a manual intervention since Spotify doesn't have a public API for installation
        print("Please download and install Spotify from https://www.spotify.com/download/windows/")
    elif platform.system() == 'Darwin':
        # For macOS systems, use Homebrew to install Spotify
        subprocess.call(['brew', 'install', '--cask', 'spotify'])
    else:
        print("Unsupported operating system.")
        return False
    return True