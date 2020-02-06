import requests
from BasicWebParser import Logins
from bs4 import BeautifulSoup
import json
import vlc
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import glob
import shutil, os, tqdm, sys
from iTunesManipulator import (iTunes, Editor, iTunesSearch)
from Features import help
import speech_recognition as sr
import SpeechAnalysis
import time
from Youtube import Youtube
import random
from speechPrompts import computer
from Player import jukebox


# Change log
# Cboin v 1.0.2.1 -- patched itunes search api not returning track names.  Also patched to use latest ytmp3 html.
# Cboin v 1.0.2 -- youtubetomp3 website tag changed to target=_blank,
# made download smarter by retrying if taking too long

# Cboin v 1.0.1 -- released to lakes computer for tests.
# Added smart search to include artists, and multi song searches.
# Also added autoDownload mode to be fully functional

# Cboin v 1.0 -- added iTunesSearch functionality and worked on excpetion handling w/ try catch / userinput

def namePlates(argument, argument2, debugMode, OS):
    print("================================")
    print("=-Welcome to the cBoin JukeBox-=")


    if argument == True:
        print("=------Automated Edition-------=")


    if argument == False:
        print("=--------Select Edition--------=")

    if argument2 == True:
        print("=------Voice Edition Beta------=")
        if OS == 'darwin':
            os.system('say "Welcome to the c boin Jukebox."')

    if debugMode == True:
        print("=----------Debug Mode----------=")

    if OS == 'darwin':
        print("=---------For MAC OS X---------=")

    if OS == 'win32':
        print("=---------For Windows----------=")

    print("=-----------V1.0.2.2-----------=")
    print("================================")

    return OS


def formatFileName(pathToFile, sliceKey, stringToAdd):
    # very last thing to do is to add "_complt" to the mp3.  This indicated it has gone through the entire process
    indexToInsertBefore = pathToFile.find(sliceKey)
    formattedSongName = pathToFile[:indexToInsertBefore] + stringToAdd + pathToFile[indexToInsertBefore:]
    os.rename(pathToFile, formattedSongName)
    return formattedSongName


# this function allows the module to be ran with or without itunes installed.
# if iTunes is not installed, the files are tagged and stored in dump folder.
def runMainWithOrWithoutItunes(microPhone,
                                recognizer,
                                iTunesInstalled=True,
                                searchFor='',
                                autoDownload=False,
                                pathToDirectory='',
                                iTunesPaths={},
                                speechRecogOn=False,
                                debugMode=False):
    localDumpFolder = os.path.join(pathToDirectory, 'dump')
    pathToSettings = os.path.join(pathToDirectory, 'settings.json')
    if iTunesInstalled == True:
        if iTunes.check_iTunes_for_song(iTunesPaths, autoDownload, speechRecogOn, pathToDirectory) == True:
            return

    if speechRecogOn == True:
        responseText = SpeechAnalysis.main(microPhone,
                                            recognizer,
                                            talking=True,
                                            OS=sys.platform,
                                            string_to_say="Would you like to download %s" %(searchFor),
                                            file_to_play=os.path.join(pathToDirectory, 'speechPrompts', 'wouldyouDL.m4a'),
                                            pathToDirectory=pathToDirectory)
        if 'yes' in responseText: # check if user wants to download or not
            computer.speak(sys.platform, 'Downloading.', os.path.join(pathToDirectory, 'speechPrompts', 'downloading.m4a'))
            autoDownload=True # perform autodownload for that songs
        else:
            return

    response = Youtube.getYoutubeInfoFromDataBase(searchQuery={'search_query':''}, songName=searchFor)
    youtubeResponseObject = Youtube.youtubeSongDownload(youtubePageResponse=response,
                                                        autoDownload=autoDownload,
                                                        pathToDumpFolder=localDumpFolder,
                                                        pathToSettings=pathToSettings,
                                                        debugMode=debugMode)

    # youtubeSongDownload returns none if there is no songPath or if user wants a more specific search
    while youtubeResponseObject['error'] == '404':
        searchFor = input('Please enter your more specific song: ')
        newYoutubeResponseAsResultOfSearch = Youtube.getYoutubeInfoFromDataBase(searchQuery={'search_query':''}, songName=searchFor)
        youtubeResponseObject = Youtube.youtubeSongDownload(youtubePageResponse=newYoutubeResponseAsResultOfSearch,
                                                autoDownload=autoDownload,
                                                pathToDumpFolder=localDumpFolder,
                                                pathToSettings=pathToSettings,
                                                debugMode=debugMode)

    # No none type is good news.. continue as normal
    if youtubeResponseObject['songPath'] != None and youtubeResponseObject['error'] == None:
        if speechRecogOn == True:
            computer.speak(sys.platform, 'Playing song.', os.path.join(pathToDirectory, 'speechPrompts', 'playingSong.m4a'))
        p = vlc.MediaPlayer(youtubeResponseObject['songPath'])
        time.sleep(1.5) #startup time
        p.play()

        trackProperties = iTunesSearch.parseItunesSearchApi(searchVariable=searchFor,
                                                            limit=10, entity='song',
                                                            autoDownload=autoDownload)

        # this checks to see if the user is happy with the song, only if in select edition
        if autoDownload == False or speechRecogOn == False:
            continueToSaveOrNot = input("Hit enter if this sounds right. To try another song -- enter (no): ")

            if continueToSaveOrNot == 'no':
                print('Returning to beginning.')
                p.stop()
                return runMainWithOrWithoutItunes(microPhone=microPhone,
                                                    recognizer=recognizer,
                                                    iTunesInstalled=iTunesInstalled,
                                                    searchFor=searchFor,
                                                    autoDownload=autoDownload,
                                                    pathToDirectory=pathToDirectory,
                                                    iTunesPaths=iTunesPaths,
                                                    speechRecogOn=speechRecogOn,
                                                    debugMode=debugMode)

        # parseItunesSearchApi() throws None return type if the user selects no properties
        if trackProperties != None:
            properSongName = iTunesSearch.mp3ID3Tagger(mp3Path=youtubeResponseObject['songPath'],
                                                        dictionaryOfTags=trackProperties)

        else:
            print('Skipping tagging process (No itunes properties selected)')

        if iTunesInstalled == True:

            # autoDownload check
            if autoDownload == False:
                userInput = input("Type 's' to save to itunes, anything else to save locally to 'dump' folder. ")
                p.stop()

            elif speechRecogOn==True and autoDownload == True: # speech recog check for save
                jukebox.wait_until_end(p, 'Type ctrl c to stop playing.')
                p.stop()
                save_or_not = SpeechAnalysis.main(microPhone,
                                                  recognizer,
                                                  talking=True,
                                                  OS=sys.platform,
                                                  string_to_say="Should I save to iTunes?",
                                                  file_to_play=os.path.join(pathToDirectory, 'speechPrompts', 'shouldSaveToItunes.m4a'),
                                                  pathToDirectory=pathToDirectory)
                if 'yes' in save_or_not:
                    userInput = 's'
                    computer.speak(sys.platform, 'Saving to Itunes.', os.path.join(pathToDirectory, 'speechPrompts', 'savingiTunes.m4a'))

                else:
                    userInput = ''
                    computer.speak(sys.platform, 'Saving Locally', os.path.join(pathToDirectory, 'speechPrompts', 'savingLocal.m4a'))

            else:
                print("Saving to iTunes.. whether you like it or not.")
                userInput = 's'
                p.stop()

            if userInput == 's':
                formattedSongName = formatFileName(pathToFile=youtubeResponseObject['songPath'], sliceKey=".mp3", stringToAdd="_complt")
                shutil.move(formattedSongName, iTunesPaths['autoAdd'])
                print("Moved your file to iTunes.")

            else:
                print("Saved your file locally.")
                p.stop()
                formattedSongName = formatFileName(pathToFile=youtubeResponseObject['songPath'], sliceKey=".mp3", stringToAdd="_complt")

            return

        else:
            # autoDownload check
            if autoDownload == False:
                jukebox.wait_until_end(p, 'Type ctrl c to stop playing.')
            elif speechRecogOn == True and autoDownload == True:
                jukebox.wait_until_end(p, 'Type ctrl c to stop playing.')
                computer.speak(sys.platform, 'Saving Locally', os.path.join(pathToDirectory, 'speechPrompts', 'savingLocal.m4a'))
            else:
                print("Saving locally. Whether you like it or not.")
            p.stop()
            formattedSongName = formatFileName(pathToFile=youtubeResponseObject['songPath'], sliceKey=".mp3", stringToAdd="_complt")
            return
    if youtubeResponseObject['error'] == 'youMP3fail':
        print("YoutubeMp3 failed too many times. quitting to last menu.")
        return

# 'auto' argv will get first video.  Manual will allow user to select video.. default behaviour
# pass argv to youtubeSongDownload
def main(argv='', r=None, mic=None, pathToItunesAutoAdd={}, speechRecog=False, debugMode = False):
    autoDownload = False
    searchList = []

    # get the obsolute file path for the machine running the script
    pathToDirectory= os.path.dirname(os.path.realpath(__file__))
    localDumpFolder = os.path.join(pathToDirectory, 'dump')
    pathToSettings = os.path.join(pathToDirectory, 'settings.json')
    with open(pathToSettings, 'r') as in_file:
        musicPlayerSettings = json.loads(in_file.read())
    #initialize dump directory
    if not os.path.exists(localDumpFolder):
        os.makedirs(localDumpFolder)

    # check for running version
    if len(argv) > 1:
        if argv[1] == 'auto':
            autoDownload = True
        if 'voice' in argv and 'debug' in argv:
            speechRecog = True
            debugMode = True
        if 'voice' in argv:
            speechRecog = True
        if len(argv) > 2 and argv[1] == 'auto' and argv[2] == 'debug':
            autoDownload = True
            debugMode = True
        if argv[1] == 'debug':
            debugMode = True

    # initialize for speechRecog
    if speechRecog == True:
        mic = sr.Microphone()
        r = sr.Recognizer()

    # determine which OS we are operating on.  Work with that OS to set
    operatingSystem = namePlates(autoDownload, speechRecog, debugMode, sys.platform)

    continueGettingSongs = 'yes' # initialize to yes in order to trigger idle listening
    continueEditing = ''
    editorOrSongDownload = ''
    searchFor = ''
    # editor functionality -- alpha test.. doesnt quite work. rest of code is in Editor.py
    # while editorOrSongDownload != 'quit':
    #
    #    editorOrSongDownload = input("Type 0 to edit, 1 to download songs, 'quit' to quit: ")
    # indent the below code and uncomment above to put editor functionality in,
    # and paste 'and editorOrSongDownload == '1'' into while loop condition

    while continueGettingSongs != 'no' :
        # initialize searchList to empty each iteration
        searchList = []
        if speechRecog == False:
            searchFor = input("Enter song(s) [song1; song2], 'instr' to view instructions OR 'set' to edit settings: ")

            if searchFor == 'set':
                help.editSettings(pathToSettings=pathToSettings)
            elif searchFor == 'instr':
                help.view_instructions(os.path.join(pathToDirectory, 'Instructions.txt'))
            else:
                searchList = searchFor.split('; ')

        # run the speechRecog edition -- BETA
        else:

            if continueGettingSongs == "yes": # idly listen if user say's yes otherwise use searchList from end of loop
                while True:
                    speechResponse = SpeechAnalysis.main(mic, r, talking=False)
                    if 'hello' in speechResponse:
                        break

                    if 'play' == speechResponse[0].split(' ')[0]: #shortcut -- skip the hello
                        speechResponse[0] = speechResponse[0].replace('play ', '') # strip play
                        searchList = speechResponse
                        break
                if 'hello' in speechResponse:
                    searchList = SpeechAnalysis.main(mic,
                                                     r,
                                                     talking=True,
                                                     OS=operatingSystem,
                                                     string_to_say="I am listening.",
                                                     file_to_play=os.path.join(pathToDirectory, 'speechPrompts', 'listening.m4a'),
                                                     pathToDirectory=pathToDirectory)
            else:
                searchList = list(nextSongs) # get the next songs from previous iteration
        # take a list of songs
        for searchForSong in searchList:
            print(" - Running program for: ", searchForSong)
            iTunesPaths = iTunes.setItunesPaths(operatingSystem, searchFor=searchForSong)
            # secret command for syncing with gDrive files.  Special feature!
            if searchFor == '1=1':
                Editor.syncWithGDrive(gDriveFolderPath=musicPlayerSettings["gDrive"]["gDriveFolderPath"],
                                      iTunesAutoAddFolderPath=iTunesPaths['autoAdd'])
                break
            # '*.*' means anyfilename, anyfiletype
            # /*/* gets through artist, then album or itunes folder structure
            if iTunesPaths == None:
                runMainWithOrWithoutItunes(microPhone=mic,
                                            recognizer=r,
                                            iTunesInstalled=False,
                                            searchFor=searchForSong,
                                            autoDownload=autoDownload,
                                            pathToDirectory=pathToDirectory,
                                            iTunesPaths=iTunesPaths,
                                            speechRecogOn=speechRecog,
                                            debugMode=debugMode)

            else:
                runMainWithOrWithoutItunes(microPhone=mic,
                                            recognizer=r,
                                            iTunesInstalled=True,
                                            searchFor=searchForSong,
                                            autoDownload=autoDownload,
                                            pathToDirectory=pathToDirectory,
                                            iTunesPaths=iTunesPaths,
                                            speechRecogOn=speechRecog,
                                            debugMode=debugMode)

            print('=----------Done Cycle--------=')

        if speechRecog == False:
            continueGettingSongs = input('Want to go again (yes/no): ')

        if speechRecog == True:
            nextSongs = [] # initialize to empty before ech speech read
            nextSongs = SpeechAnalysis.main(mic,
                                                  r,
                                                  talking=True,
                                                  OS=operatingSystem,
                                                  string_to_say='Say another song or no to quit.',
                                                  file_to_play=os.path.join(pathToDirectory, 'speechPrompts', 'anotherone.m4a'),
                                                  pathToDirectory=pathToDirectory)
            continueGettingSongs = nextSongs[0] # set first word to continueGettingSongs to check if they said yes or no

    # editor functionality goes here (from iTunesManipulator.Editor)
    print("================================")
    print("=--------Have a fine day-------=")
    print("================================")
    if speechRecog == True and operatingSystem=='darwin':
        computer.speak(operatingSystem, 'Goodbye.')

if __name__=="__main__":
    main(sys.argv)
