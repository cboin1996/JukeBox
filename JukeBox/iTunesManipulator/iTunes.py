import os, sys
import vlc
import time
import random
import glob
from Youtube import Youtube
from speechPrompts import computer
from Player import jukebox
from iTunesManipulator import iTunesSearch
from Features import tools

PLAYING_STRING_DEFAULT = "Playing: %s - %s: %s."
PLAYING_STRING_COMMANDS_DEFAULT = "\nCommands:\n - q (stop),\n - space (pause/resume),\n - a (restart),\n - z (previous)"
PLAYING_STRING_COMMANDS_SPECIAL = PLAYING_STRING_COMMANDS_DEFAULT + "\n - d (next)"

""" Returns True is song is found/research/skip, else false """
def check_iTunes_for_song(iTunesPaths,
                          autoDownload,
                          speechRecogOn=None,
                          pathToDirectory='',
                          command='',
                          mic=None,
                          r=None):
    artists = [] # will hold list of artists
    songNames = [] # need to be zeroed out here DO NOT MOVE into parameter.
    albums = []
    if len(iTunesPaths['searchedSongResult']) == 0:
        print("File not found in iTunes Library.. Getting From Youtube")
        return False
    else:
        # get the first item of the songs returned from the list of song paths matching
        # plays song immediatly, so return after this executes
        print("Here are song(s) in your library matching your search: ")
        i = 0

        for songPath in iTunesPaths['searchedSongResult']:
            songName = songPath.split(os.sep)
            artists.append(songName[len(songName)-3])
            albums.append(songName[len(songName)-2])
            songNames.append(songName[len(songName)-1])
            print('  %d \t- %s - %s: %s' % (i, albums[i], artists[i], songNames[i]))
            i += 1

        # autoDownload condition
        if autoDownload == True:
            print("Song name too similar to one or more of above! Skipping.")
            return True

        if speechRecogOn == False:
            print('Which one(s) do you want to hear (e.g. 0 1 3)?')
            user_input_string = "OR type 'you' (search youtube), 'ag' (search again/skip), 'sh' (shuffle), 'pl' (play in order), '406' (return home): "
            songSelection = iTunesSearch.choose_items(input_string=user_input_string, props_lyst=iTunesPaths['searchedSongResult'])

        if speechRecogOn == True and command == 'shuffle':
            songSelection = 'sh'

        elif speechRecogOn == True and command == 'all':
            songSelection = 'pl'

        elif speechRecogOn == True and command == 'play':
            iTunesPaths['searchedSongResult'] = [iTunesPaths['searchedSongResult'][0]] # select first song, data requires list
            play_in_order(iTunesPaths, speechRecogOn, pathToDirectory, "Single Mode Activated", 'singleModeOn.m4a', mic=mic, r=r, command_string=PLAYING_STRING_COMMANDS_SPECIAL)
            return True
        if songSelection == 'ag':
            print('Returning to beginning.')
            return True
        if songSelection == '406':
            print("Exiting to home.")
            return '406'

        # shuffle algorithm TODO: move to a function
        if songSelection == 'sh':
            random.shuffle(iTunesPaths['searchedSongResult'])
            play_in_order(iTunesPaths, speechRecogOn, pathToDirectory, "Shuffle Mode Activated", 'shuffleModeOn.m4a', mic=mic, r=r, command_string=PLAYING_STRING_COMMANDS_SPECIAL)
            return True

        elif songSelection == 'you':
            return False

        elif songSelection == 'pl':
            play_in_order(iTunesPaths, speechRecogOn, pathToDirectory, "Ordered Mode Activated", 'orderModeOn.m4a', mic=mic, r=r, command_string=PLAYING_STRING_COMMANDS_SPECIAL)
            return True

        # play the song(s) only if they want, otherwise continute with program.
        else:
            if speechRecogOn == False:
                iTunesPaths['searchedSongResult'] = songSelection
                play_in_order(iTunesPaths, speechRecogOn, pathToDirectory, mic=mic, r=r)

            return True

def play_in_order(iTunesPaths, speechRecogOn, pathToDirectory, speech_string='', speech_path='', mic=None, r=None, command_string=''):

    wait_until_end = ''
    if speechRecogOn == True:
        computer.speak(sys.platform,
                       speech_string,
                       os.path.join(pathToDirectory, 'speechPrompts', speech_path)
                       )
    print(PLAYING_STRING_COMMANDS_DEFAULT) # provide commands
    i = 0
    while i < len(iTunesPaths['searchedSongResult']):
        song = iTunesPaths['searchedSongResult'][i].split(os.sep)
        if speechRecogOn == True:
            computer.speak(sys.platform,
                           "Playing: %s." % (tools.stripFileForSpeech(song[len(song)-1])),
                           os.path.join(pathToDirectory, 'speechPrompts', 'playingSong.m4a')
                           )
        wait_until_end = jukebox.play_file(PLAYING_STRING_DEFAULT % (song[len(song)-3], #3 is album
                                                                     song[len(song)-2], #2 is artist
                                                                     song[len(song)-1]), #1 is song
                                                                     iTunesPaths['searchedSongResult'][i],
                                                                     song_index=i,
                                                                     index_diff=len(iTunesPaths['searchedSongResult'])-i,
                                                                     mic=mic, r=r, speechRecogOn=speechRecogOn,
                                                                     command_string=PLAYING_STRING_COMMANDS_SPECIAL)
        if wait_until_end == 'rewind' and i != 0: # break loop if user desires it to be.
            i = i-1 # play previous

        if wait_until_end == 'next':
            i = i+1 # play next song
        if wait_until_end == 'quit': # break loop if user desires it to be.
            break # quit

def setItunesPaths(operatingSystem, iTunesPaths={'autoAdd':'', 'searchedSongResult':[]}, searchFor=''):
    iTunesPaths['searchedSongResult'] = []

    if operatingSystem == 'darwin':
        pathToItunesAutoAdd = os.path.join('/Users', '*', 'Music', 'iTunes', 'iTunes Media', 'Automatically Add to Music.localized')
        addToItunesPath = glob.glob(pathToItunesAutoAdd, recursive=True)

        if len(addToItunesPath) == 0:
            print('You do not have iTunes installed on this machine. Continueing without.')
            return None

        iTunesPaths['autoAdd'] = addToItunesPath[0]
        # '*.*' means anyfilename, anyfiletype
        # /*/* gets through artist, then album or itunes folder structure
        # iTUNES LIBRARY SEARCH ALGORITHM -- returns lists of matches
        pathToSong = os.path.join('/Users', '*', 'Music', 'iTunes', 'iTunes Media', 'Music', '*', '*','*.*')
        path = glob.glob(pathToSong, recursive=True)

        iTunesPaths = iTunesLibSearch(songPaths=path, iTunesPaths=iTunesPaths, searchParameters=searchFor)

    elif operatingSystem == 'win32':
        pathToItunesAutoAdd = os.path.join('C:', os.sep, 'Users', '*', 'Music', 'iTunes', 'iTunes Media', 'Automatically Add to iTunes')
        addToItunesPath = glob.glob(pathToItunesAutoAdd, recursive=True)

        if len(addToItunesPath) == 0:
            print('You do not have iTunes installed on this machine. Continueing without.')
            return None

        iTunesPaths['autoAdd'] = addToItunesPath[0]

        # '*.*' means anyfilename, anyfiletype
        # /*/* gets through artist, then album or itunes folder structure
        # iTUNES LIBRARY SEARCH ALGORITHM -- returns lists of matches
        pathToSong = os.path.join('C:', os.sep, 'Users', '*', 'Music', 'iTunes', 'iTunes Media', 'Music', '*', '*', '*.*')
        path = glob.glob(pathToSong, recursive=True)

        iTunesPaths = iTunesLibSearch(songPaths=path, iTunesPaths=iTunesPaths, searchParameters=searchFor)

    else:
        print("Unrecognized OS. No Itunes recognizable.")
        return None

    return iTunesPaths

def iTunesLibSearch(songPaths, iTunesPaths={}, searchParameters=''):

    for songPath in songPaths:
        songNameSplit = songPath.split(os.sep)
        formattedName = songNameSplit[len(songNameSplit)-1].lower() + " " + songNameSplit[len(songNameSplit)-2].lower() + " " + songNameSplit[len(songNameSplit)-3].lower()
        formattedName = Youtube.removeIllegalCharacters(formattedName)
        searchParameters = Youtube.removeIllegalCharacters(searchParameters)
        # songNameSplit is list of itunes file path.. artist is -3 from length, song is -1
        if searchParameters.lower() in formattedName.lower():
            iTunesPaths['searchedSongResult'].append(songPath)
    iTunesPaths['searchedSongResult'] = sorted(iTunesPaths['searchedSongResult'])
    return iTunesPaths
