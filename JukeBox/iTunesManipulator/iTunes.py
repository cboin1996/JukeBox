import os, sys
import vlc
import time
import random
import glob
from Youtube import Youtube
from speechPrompts import computer
from Player import jukebox

""" Returns True is song is found, else false """
def check_iTunes_for_song(iTunesPaths,
                          autoDownload,
                          speechRecogOn,
                          pathToDirectory=''):
    artists = [] # will hold list of artists
    songNames = [] # need to be zeroed out here DO NOT MOVE into parameter.
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
            songNames.append(songName[len(songName)-1])
            print('  %d \t- %s: %s' % (i, artists[i], songNames[i]))
            i += 1

        # autoDownload condition
        if autoDownload == True:
            print("Song name too similar to one or more of above! Skipping.")
            return True

        if speechRecogOn == False:
            print('Which one do you want to hear?')
            songSelection = input("Type 'you' to search youtube instead. 'ag' to search again. 'sh' to shuffle through the list: ")

        if speechRecogOn == True:
            if len(iTunesPaths['searchedSongResult']) > 1:
                songSelection = 'sh'
            else:
                songSelection = 0

        if songSelection == 'ag':
            print('Returning to beginning.')
            return True

        # play the song only if they want, otherwise continute with program.
        if songSelection != 'you' and songSelection != 'sh':
            songSelection = int(songSelection)
            while songSelection not in range(0, len(iTunesPaths['searchedSongResult'])):
                songSelection = int(input('Invalid Input. Try Again'))

            if speechRecogOn == True:
                computer.speak(sys.platform,
                               "Playing: %s." % (songNames[songSelection].replace('.mp3', '')),
                               os.path.join(pathToDirectory, 'speechPrompts', 'playingSong.m4a')
                               )

            jukebox.play_file("Playing: %s - %s. ctrl c to stop." % (artists[songSelection], songNames[songSelection]),
                              iTunesPaths['searchedSongResult'][songSelection])
            return True

        # shuffle algorithm TODO: move to a function
        if songSelection == 'sh':
            shuffle(iTunesPaths, speechRecogOn, pathToDirectory)

            return True

def shuffle(iTunesPaths, speechRecogOn, pathToDirectory):
    consec_skips = 0
    prev_wait_unt_end = False
    if speechRecogOn == True:
        computer.speak(sys.platform,
                       "Shuffle mode activated.",
                       os.path.join(pathToDirectory, 'speechPrompts', 'shuffleModeOn.m4a')
                       )
    while len(iTunesPaths['searchedSongResult']) - 1 >= 0:
        songSelection = random.randint(0, len(iTunesPaths['searchedSongResult']) - 1)
        tempItunesSong = iTunesPaths['searchedSongResult'][songSelection].split(os.sep)
        if speechRecogOn == True:
            computer.speak(sys.platform,
                           "Playing: %s." % (tempItunesSong[len(tempItunesSong)-1]),
                           os.path.join(pathToDirectory, 'speechPrompts', 'playingSong.m4a')
                           )
        wait_until_end = jukebox.play_file("Playing: %s - %s. ctrl c to stop playing... " % (tempItunesSong[len(tempItunesSong)-3],tempItunesSong[len(tempItunesSong)-1]),
                                                                                             iTunesPaths['searchedSongResult'][songSelection])
        if wait_until_end == False and prev_wait_unt_end == False: # check that user has skipped song
            consec_skips += 1
        else:
            consec_skips = 0

        if consec_skips >= 3:
            return
        prev_wait_unt_end = wait_until_end

        iTunesPaths['searchedSongResult'].remove(iTunesPaths['searchedSongResult'][songSelection])


def iTunesLibSearch(songPaths, iTunesPaths={}, searchParameters=''):

    for songPath in songPaths:
        songNameSplit = songPath.split(os.sep)
        formattedName = songNameSplit[len(songNameSplit)-1].lower() + songNameSplit[len(songNameSplit)-3].lower()
        formattedName = Youtube.removeIllegalCharacters(formattedName)
        # songNameSplit is list of itunes file path.. artist is -3 from length, song is -1
        if searchParameters.lower() in formattedName.lower():
            iTunesPaths['searchedSongResult'].append(songPath)

    return iTunesPaths

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
