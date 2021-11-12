import os, sys
import vlc
import time
import random
import glob
from youtube import youtube
from speechprompts import computer
from player import jukebox
from itunes import search
from features import tools
import globalvariables
import json
def setItunesPaths(operatingSystem, iTunesPaths={'autoAdd':'', 'searchedSongResult':[]}, searchFor='', album_properties=None):
    """
    Determines whether iTunes is installed on the computer, and generates path to
    the automatically add to iTunes folder
    params: operating system from sys.platform, iTunesPaths dictionary object, song to search iTunes for
    Returns: object with path to automatically add to iTunes folder and songs matching
            user's search
    """
    iTunesPaths['searchedSongResult'] = []
    path_to_settings = os.path.join(sys.path[0], 'settings.json')

    with open(path_to_settings, 'r') as f:
        settings_json = json.load(f)
    if operatingSystem == 'darwin':
        pathToItunesAutoAdd = os.path.join('/Users', '*', 'Music', 'iTunes', 'iTunes Media', 'Automatically Add to Music.localized')
        pathToSong = os.path.join('/Users', '*', 'Music', 'iTunes', 'iTunes Media', 'Music', '*', '*','*.*')
    elif operatingSystem == 'win32':
        if os.path.exists(settings_json["iTunes"]["iTunesAutoPath"]) and os.path.exists(settings_json["iTunes"]["iTunesBasePath"]):
            if settings_json["iTunes"]["iTunesSongsPath"] == "":
                with open(path_to_settings, 'w') as f:
                    settings_json["iTunes"]["iTunesSongsPath"] = os.path.join(settings_json["iTunes"]["iTunesBasePath"], "Music", "*", "*", "*.*")
                    json.dump(settings_json, f)
            pathToItunesAutoAdd = settings_json["iTunes"]["iTunesAutoPath"]
            pathToSong = settings_json["iTunes"]["iTunesSongsPath"]
        else:
            pathToItunesAutoAdd = os.path.join('C:', os.sep, 'Users', '*', 'Music', 'iTunes', 'iTunes Media', 'Automatically Add to iTunes')
            pathToSong = os.path.join('C:', os.sep, 'Users', '*', 'Music', 'iTunes', 'iTunes Media', 'Music', '*', '*', '*.*')
    else:
        print("Unrecognized OS. No Itunes recognizable.")
        return None
    addToItunesPath = glob.glob(pathToItunesAutoAdd, recursive=True)
    if len(addToItunesPath) == 0:
        
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
                iTunesPaths['autoAdd'] = path # set variables for successful continue of program..  
                pathToSong = os.path.join(song_path, '*', '*', '*.*')
            else:
                settings_json["iTunes"]["userWantsiTunes"] = 'n'
                with open(path_to_settings, 'w') as f:
                    json.dump(settings_json, f)
                return None
        else:
            return None
    else:
        iTunesPaths['autoAdd'] = addToItunesPath[0]
        # '*.*' means anyfilename, anyfiletype
        # /*/* gets through artist, then album or itunes folder structure
        # iTUNES LIBRARY SEARCH ALGORITHM -- returns lists of matches
    path = glob.glob(pathToSong, recursive=True)
    iTunesPaths = iTunesLibSearch(songPaths=path, iTunesPaths=iTunesPaths, searchParameters=searchFor, album_properties=album_properties)
    return iTunesPaths


def iTunesLibSearch(songPaths, iTunesPaths={}, searchParameters='', album_properties=None):
    """
    Performs a search on users iTunes library by album, artist and genre
    params: 
    songPaths: paths to all iTunes songs
    iTunesPaths: iTunes dictionary object
    searchParameters: search term
    album_properties: determines whether to do a smarter search based on given album properties
    Returns: iTunesPaths dict with songs matching the search added 
    """
    for songPath in songPaths:
        songNameSplit = songPath.split(os.sep)
        song_name = Youtube.removeIllegalCharacters(songNameSplit[len(songNameSplit)-1].lower())
        album_name = Youtube.removeIllegalCharacters(songNameSplit[len(songNameSplit)-2].lower())
        artist_name = Youtube.removeIllegalCharacters(songNameSplit[len(songNameSplit)-3].lower())
        searchParameters = Youtube.removeIllegalCharacters(searchParameters.lower())
        if album_properties == None: 
            formattedName = song_name + " " + album_name + " " + artist_name
            # songNameSplit is list of itunes file path.. artist is -3 from length, song is -1
            if searchParameters in formattedName:
                iTunesPaths['searchedSongResult'].append(songPath)
        else:
            if album_properties[GlobalVariables.artist_name].lower() in artist_name and searchParameters in song_name:
                iTunesPaths['searchedSongResult'].append(songPath)
    iTunesPaths['searchedSongResult'] = sorted(iTunesPaths['searchedSongResult']) # sort tracks alphabetically
    return iTunesPaths
