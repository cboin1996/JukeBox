import os, sys
import vlc
import time
import random
import glob
import json
import pydub
from webparse import updates

from youtube import youtube
from speechprompts import computer
from player import jukebox
from itunes import search
from features import tools
import globalvariables
def set_itunes_path(operating_system, itunes_paths={'autoAdd':'', 'searchedSongResult':[]}, search_for='', album_properties=None):
    """
    Determines whether iTunes is installed on the computer, and generates path to
    the automatically add to iTunes folder
    params: operating system from sys.platform, iTunesPaths dictionary object, song to search iTunes for
    Returns: object with path to automatically add to iTunes folder and songs matching
            user's search
    """
    itunes_paths['searchedSongResult'] = []
    path_to_settings = os.path.join(sys.path[0], 'settings.json')

    with open(path_to_settings, 'r') as f:
        settings_json = json.load(f)
    if operating_system == 'darwin':
        path_to_itunes_auto_add = os.path.join('/Users', '*', 'Music', 'iTunes', 'iTunes Media', 'Automatically Add to Music.localized')
        path_to_song = os.path.join('/Users', '*', 'Music', 'iTunes', 'iTunes Media', 'Music', '*', '*','*.*')
    elif operating_system == 'win32':
        if os.path.exists(settings_json["iTunes"]["iTunesAutoPath"]) and os.path.exists(settings_json["iTunes"]["iTunesBasePath"]):
            if settings_json["iTunes"]["iTunesSongsPath"] == "":
                with open(path_to_settings, 'w') as f:
                    settings_json["iTunes"]["iTunesSongsPath"] = os.path.join(settings_json["iTunes"]["iTunesBasePath"], "Music", "*", "*", "*.*")
                    json.dump(settings_json, f)
            path_to_itunes_auto_add = settings_json["iTunes"]["iTunesAutoPath"]
            path_to_song = settings_json["iTunes"]["iTunesSongsPath"]
        else:
            path_to_itunes_auto_add = os.path.join('C:', os.sep, 'Users', '*', 'Music', 'iTunes', 'iTunes Media', 'Automatically Add to iTunes')
            path_to_song = os.path.join('C:', os.sep, 'Users', '*', 'Music', 'iTunes', 'iTunes Media', 'Music', '*', '*', '*.*')
    else:
        print("Unrecognized OS. No Itunes recognizable.")
        return None
    add_to_itunes_path = glob.glob(path_to_itunes_auto_add, recursive=True)
    if len(add_to_itunes_path) == 0:
        
        if settings_json["iTunes"]['userWantsiTunes'] == 'y':
            is_iTunes_installed = input("I can't find your iTunes.. do you have it installed in some random path baudy [y/n]? ")
            while (is_iTunes_installed != 'y' and is_iTunes_installed != 'n'):
                is_iTunes_installed = input('Stop messing around and say "y" or "n" [y/n]? ')  
        
            if is_iTunes_installed == 'y':
                
                valid_path = False

                while valid_path == False:
                    path = input("Set your path to your iTunes auto add folder: ")
                    song_path = input("Set your path to where your iTunes songs are stored: ")

                    path = path.strip()
                    song_path = song_path.strip()

                    if os.path.exists(path):
                        if os.path.exists(song_path):
                            valid_path = True

                settings_json["iTunes"]["iTunesAutoPath"] = path
                settings_json["iTunes"]["iTunesBasePath"] = song_path
                settings_json["iTunes"]["iTunesSongsPath"] = os.path.join(song_path, '*', '*', '*.*')
                with open (path_to_settings, 'w') as f:
                    json.dump(settings_json, f)
                itunes_paths['autoAdd'] = path # set variables for successful continue of program..  
                path_to_song = os.path.join(song_path, '*', '*', '*.*')
            else:
                settings_json["iTunes"]["userWantsiTunes"] = 'n'
                with open(path_to_settings, 'w') as f:
                    json.dump(settings_json, f)
                return None
        else:
            return None
    else:
        itunes_paths['autoAdd'] = add_to_itunes_path[0]
        # '*.*' means anyfilename, anyfiletype
        # /*/* gets through artist, then album or itunes folder structure
        # iTUNES LIBRARY SEARCH ALGORITHM -- returns lists of matches
    path = glob.glob(path_to_song, recursive=True)
    itunes_paths = itunes_lib_search(song_paths=path, itunes_paths=itunes_paths, search_parameters=search_for, album_properties=album_properties)
    return itunes_paths

def convert_mp3_to_itunes_format(input_filename):
    """Convert the mp3 file to itunes format, updating tags to the new itunes standard.

    Args:
        input_filename (str): the full path of the file

    Returns:
        str: the path to the modified file.
    """
    pydub.AudioSegment.ffmpeg = updates.get_path_to_ffmpeg()
    song_file = pydub.AudioSegment.from_mp3(input_filename)
    output_filename = input_filename.replace(".mp3", ".m4a")
    song_file.export(output_filename, format="ipod")
    return output_filename

def itunes_lib_search(song_paths, itunes_paths={}, search_parameters='', album_properties=None):
    """
    Performs a search on users iTunes library by album, artist and genre
    params: 
    songPaths: paths to all iTunes songs
    iTunesPaths: iTunes dictionary object
    searchParameters: search term
    album_properties: determines whether to do a smarter search based on given album properties
    Returns: iTunesPaths dict with songs matching the search added 
    """
    for song_path in song_paths:
        song_name_split = song_path.split(os.sep)
        song_name = youtube.remove_illegal_characters(song_name_split[len(song_name_split)-1].lower())
        album_name = youtube.remove_illegal_characters(song_name_split[len(song_name_split)-2].lower())
        artist_name = youtube.remove_illegal_characters(song_name_split[len(song_name_split)-3].lower())
        search_parameters = youtube.remove_illegal_characters(search_parameters.lower())
        if album_properties == None: 
            formattedName = song_name + " " + album_name + " " + artist_name
            # songNameSplit is list of itunes file path.. artist is -3 from length, song is -1
            if search_parameters in formattedName:
                itunes_paths['searchedSongResult'].append(song_path)
        else:
            if album_properties[globalvariables.artist_name].lower() in artist_name and search_parameters in song_name:
                itunes_paths['searchedSongResult'].append(song_path)
    itunes_paths['searchedSongResult'] = sorted(itunes_paths['searchedSongResult']) # sort tracks alphabetically
    return itunes_paths
