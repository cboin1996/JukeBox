import os, sys
import vlc
import time
import random
import glob
from Youtube import Youtube
from speechPrompts import computer
from Player import jukebox

PLAYING_STRING_DEFAULT = "Playing: %s - %s: %s. d (stop), space (pause/resume), a (restart), z (previous)"
PLAYING_STRING_SPECIAL = "Playing: %s - %s: %s. d (next), space (pause/resume), a (restart), z (previous), q (quit)"
""" Returns True is song is found/research/skip, else false """
def check_iTunes_for_song(iTunesPaths,
                          autoDownload,
                          speechRecogOn,
                          pathToDirectory='',
                          command=''):
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
            print('Which one do you want to hear (Type Number)?')
            songSelection = input("OR type 'you' (search youtube), 'ag' (search again/skip), 'sh' (shuffle), 'pl' (play in order): ")

        if speechRecogOn == True and command == 'shuffle':
            songSelection = 'sh'

        elif speechRecogOn == True and command == 'playall':
            songSelection = 'pl'

        elif speechRecogOn == True and command == 'play':
            songSelection = 0

        if songSelection == 'ag':
            print('Returning to beginning.')
            return True

        # shuffle algorithm TODO: move to a function
        if songSelection == 'sh':            
            random.shuffle(iTunesPaths['searchedSongResult'])
            play_in_order(iTunesPaths, speechRecogOn, pathToDirectory)
            return True

        elif songSelection == 'you':
            return False

        elif songSelection == 'pl':
            play_in_order(iTunesPaths, speechRecogOn, pathToDirectory)
            return True

        # play the song only if they want, otherwise continute with program.
        else:
            songSelection = int(songSelection)
            while songSelection not in range(0, len(iTunesPaths['searchedSongResult'])):
                songSelection = int(input('Invalid Input. Try Again'))

            if speechRecogOn == True:

                computer.speak(sys.platform,
                               "Playing: %s." % (stripFileForSpeech(songNames[songSelection])),
                               os.path.join(pathToDirectory, 'speechPrompts', 'playingSong.m4a')
                               )
            wait_until_end = jukebox.play_file(PLAYING_STRING_DEFAULT % (albums[songSelection], artists[songSelection], songNames[songSelection]),
                                               iTunesPaths['searchedSongResult'][songSelection])
            while wait_until_end != "next" and wait_until_end != None and wait_until_end != "quit":
                jukebox.play_file(PLAYING_STRING_DEFAULT % (albums[songSelection], artists[songSelection], songNames[songSelection]),
                              iTunesPaths['searchedSongResult'][songSelection])
            return True

def stripFileForSpeech(file_name):
    return file_name.replace('.mp3','').replace('&', 'and').replace('(', '').replace(')', '')

# def shuffle(iTunesPaths, speechRecogOn, pathToDirectory):
#     consec_skips = 0
#     wait_until_end = ''
#     if speechRecogOn == True:
#         computer.speak(sys.platform,
#                        "Shuffle mode activated.",
#                        os.path.join(pathToDirectory, 'speechPrompts', 'shuffleModeOn.m4a')
#                        )
#     while len(iTunesPaths['searchedSongResult']) - 1 >= 0 and wait_until_end!='quit': # quit condition
#         songSelection = random.randint(0, len(iTunesPaths['searchedSongResult']) - 1)
#         tempItunesSong = iTunesPaths['searchedSongResult'][songSelection].split(os.sep)
#         if speechRecogOn == True and consec_skips == 0:
#             computer.speak(sys.platform,
#                            "Playing: %s." % (stripFileForSpeech(tempItunesSong[len(tempItunesSong)-1])),
#                            os.path.join(pathToDirectory, 'speechPrompts', 'playingSong.m4a')
#                            )
#         # returns quit if user wnats to end the shuffle
#         wait_until_end = jukebox.play_file(PLAYING_STRING_SPECIAL % (tempItunesSong[len(tempItunesSong)-3], tempItunesSong[len(tempItunesSong)-2], #2 is artist
#                                                                      tempItunesSong[len(tempItunesSong)-1]), iTunesPaths['searchedSongResult'][songSelection])
#         iTunesPaths['searchedSongResult'].remove(iTunesPaths['searchedSongResult'][songSelection])

def play_in_order(iTunesPaths, speechRecogOn, pathToDirectory):
    consec_skips = 0
    wait_until_end = ''
    if speechRecogOn == True:
        computer.speak(sys.platform,
                       "Ordered Mode Activated",
                       os.path.join(pathToDirectory, 'speechPrompts', 'orderModeOn.m4a')
                       )
    i = 0
    while i < len(iTunesPaths['searchedSongResult']):
        song = iTunesPaths['searchedSongResult'][i].split(os.sep)
        if speechRecogOn == True and consec_skips == 0:
            computer.speak(sys.platform,
                           "Playing: %s." % (stripFileForSpeech(song[len(song)-1])),
                           os.path.join(pathToDirectory, 'speechPrompts', 'playingSong.m4a')
                           )
        wait_until_end = jukebox.play_file(PLAYING_STRING_SPECIAL % (song[len(song)-3], #3 is album
                                                                     song[len(song)-2], #2 is artist
                                                                     song[len(song)-1]), #1 is song
                                                                     iTunesPaths['searchedSongResult'][i],
                                                                     song_index=i)
        print(wait_until_end)
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
