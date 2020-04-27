import requests
from BasicWebParser import Logins, updates
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
from Features import feature, tools, gDrive
import speech_recognition as sr
import SpeechAnalysis
import time
from Youtube import Youtube
import random
from speechPrompts import computer
from Player import jukebox
import GlobalVariables


"""
Change log
Cboin v 2.1 -- Added saving to google drive option
Cboin v 2.0 -- Added album downloading, speech regonition, keybinding audio playing,
                   shuffle mode and more.
Cboin v 1.0.2.1 -- patched itunes search api not returning track names.  Also patched to use latest ytmp3 html.
Cboin v 1.0.2 -- youtubetomp3 website tag changed to target=_blank,
made download smarter by retrying if taking too long

Cboin v 1.0.1 -- released to lakes computer for tests.
Added smart search to include artists, and multi song searches.
Also added autoDownload mode to be fully functional

Cboin v 1.0 -- added iTunesSearch functionality and worked on excpetion handling w/ try catch / userinput
"""


def namePlates(argument, argument2, debugMode, OS):
    """
    Produces nameplates and determines operating system
    args: two command line argumates, debug mode on or off, operating system
    Returns: operating system
    """
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

    print("=-------------V2.1-------------=")
    print("================================")

    return OS

def formatFileName(pathToFile, sliceKey, stringToAdd):
    """
    Formats a file name signalling it is done being tagged with MP3 metadata
    args: path to the file to format, slice key to insert string tag before, string to
        add to filename
    Returns: None
    """
    # very last thing to do is to add "_complt" to the mp3.  This indicated it has gone through the entire process
    indexToInsertBefore = pathToFile.find(sliceKey)
    formattedSongName = pathToFile[:indexToInsertBefore] + stringToAdd + pathToFile[indexToInsertBefore:]
    os.rename(pathToFile, formattedSongName)
    return formattedSongName


# this function allows the module to be ran with or without itunes installed.
# if iTunes is not installed, the files are tagged and stored in dump folder.

def run_download(microPhone,
                recognizer,
                iTunesInstalled=True,
                searchFor='',
                autoDownload=False,
                pathToDirectory='',
                iTunesPaths={},
                speechRecogOn=False,
                debugMode=False,
                trackProperties={},
                musicPlayerSettings=None):
    """
    Runs the download process for a song
    args: speech recognition microphone object, speech recognition recognizer object,
        iTunes installed or note, song to search youtube for, autodownload on or not,
        path to root directory, iTunes paths with auto add and song path, speech
        recognition on or not, debug mode on or not, track properties on or not
    Returns: None
    """
    localDumpFolder = os.path.join(pathToDirectory, "dump")
    pathToSettings = os.path.join(pathToDirectory, 'settings.json')

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
    if youtubeResponseObject['error'] == '405': # return out if user wants to cancel.
        return

    # No none type is good news.. continue as normal
    if youtubeResponseObject['songPath'] != None and youtubeResponseObject['error'] == None:
        if speechRecogOn == True:
            computer.speak(sys.platform, 'Playing song.', os.path.join(pathToDirectory, 'speechPrompts', 'playingSong.m4a'))
        p = vlc.MediaPlayer(youtubeResponseObject['songPath'])
        time.sleep(1.5) #startup time
        p.play()


        # this checks to see if the user is happy with the song, only if in select edition
        if autoDownload == False and speechRecogOn == False:
            continueToSaveOrNot = input("Hit enter if this sounds right. To try another song -- enter (no): ")

            if continueToSaveOrNot == 'no':
                print('Returning to beginning.')
                p.stop()
                return run_download(microPhone=microPhone,
                                                    recognizer=recognizer,
                                                    iTunesInstalled=iTunesInstalled,
                                                    searchFor=searchFor,
                                                    autoDownload=autoDownload,
                                                    pathToDirectory=pathToDirectory,
                                                    iTunesPaths=iTunesPaths,
                                                    speechRecogOn=speechRecogOn,
                                                    debugMode=debugMode,
                                                    trackProperties=trackProperties)

        # parseItunesSearchApi() throws None return type if the user selects no properties
        if trackProperties != None:
            properSongName = iTunesSearch.mp3ID3Tagger(mp3Path=youtubeResponseObject['songPath'],
                                                        dictionaryOfTags=trackProperties)

        else:
            print('Skipping tagging process (No itunes properties selected)')

        if iTunesInstalled == True:

            # autoDownload check
            if autoDownload == False:
                userInput = input("Type 's' to save to itunes, 'g' to save to gDrive, anything else to save locally to 'dump' folder. ")
                p.stop()

            elif speechRecogOn==True and autoDownload == True: # speech recog check for save
                action = ''
                print(GlobalVariables.PLAYING_STRING_COMMANDS_DEFAULT) # provide commands
                while action != 'next': # used this block again below. Should be its own function.. but am too right now.
                    action = jukebox.wait_until_end(player=p, prompt='', file_index=0,
                                       index_diff=1, mic=microPhone, r=recognizer, speechRecogOn=speechRecogOn, command_string=GlobalVariables.PLAYING_STRING_COMMANDS_DEFAULT)
                    if action == GlobalVariables.player_stop:
                        break
                    p.play()
                p.stop()
                save_or_not = SpeechAnalysis.main(microPhone,
                                                  recognizer,
                                                  talking=True,
                                                  OS=sys.platform,
                                                  string_to_say="Should I save to iTunes?",
                                                  file_to_play=os.path.join(pathToDirectory, 'speechPrompts', 'shouldSaveToItunes.m4a'),
                                                  pathToDirectory=pathToDirectory,
                                                  expected=['yes', 'no'],
                                                  phrase_time_limit=4
                                                  )
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
            
            elif userInput == 'g':
                p.stop()
                gDrive.save_song(musicPlayerSettings['gDrive'], youtubeResponseObject['songPath'].split(os.sep)[-1], youtubeResponseObject['songPath'])

            else:
                print("Saved your file locally.")
                p.stop()
                formattedSongName = formatFileName(pathToFile=youtubeResponseObject['songPath'], sliceKey=".mp3", stringToAdd="_complt")

            return

        else:
            # autoDownload check
            if autoDownload == False:
                user_input = input("Type 'g' to save to gDrive, anything else to stop playing and save locally.")

                if user_input == 'g':
                    p.stop()

                    gDrive.save_song(musicPlayerSettings['gDrive'], youtubeResponseObject['songPath'].split(os.sep)[-1], youtubeResponseObject['songPath'])
                    return

            elif speechRecogOn == True and autoDownload == True:
                print(GlobalVariables.PLAYING_STRING_COMMANDS_DEFAULT) # provide commands
                action = ''
                while action != 'next': # wait until user ends song. 'next is returned from wait_until_end upon completion.'
                    action = jukebox.wait_until_end(player=p, prompt='', file_index=0,
                                       index_diff=1, mic=microPhone, r=recognizer, speechRecogOn=speechRecogOn, command_string=GlobalVariables.PLAYING_STRING_COMMANDS_DEFAULT)
                    if action == GlobalVariables.player_stop:
                        break
                    p.play()

                computer.speak(sys.platform, 'Saving Locally', os.path.join(pathToDirectory, 'speechPrompts', 'savingLocal.m4a'))
            else:
                print("Saving locally. Whether you like it or not.")
            p.stop()
            formattedSongName = formatFileName(pathToFile=youtubeResponseObject['songPath'], sliceKey=".mp3", stringToAdd="_complt")
            return
    if youtubeResponseObject['error'] == 'youMP3fail':
        print("YoutubeMp3 failed too many times. quitting to last menu.")
        return

def run_for_songs(mic=None, r=None, searchList=[], autoDownload=None,
                pathToDirectory=None, speechRecogOn=None, debugMode=None, command=None,
                musicPlayerSettings=None, prog_vers='', operatingSystem=None, searchFor=None,
                requiredJsonSongKeys=None, album_artist_list=None, songs_in_album_props=None):
    """
    Runs through a song search process in iTunes then youtube depending on user interaction
    args: microphone object, speech recognizer object, list of songs to search for, auto download mode on or off
        path to root script directory, speech recognition mode on or off, debug mode on or off,
        speech recognition command, program settings from json file, program version album or song download mode,
        computer operating system, song to search for, required json song keys to tag mp3's with,
        list of album artist metadata, song meta data for songs in an album
    Returns: None
    """
    for i, searchForSong in enumerate(searchList):
        print(" - Running program for: ", searchForSong)
        iTunesPaths = iTunes.setItunesPaths(operatingSystem, searchFor=searchForSong)

        # '*.*' means anyfilename, anyfiletype
        # /*/* gets through artist, then album or itunes folder structure
        if iTunesPaths == None:
            iTunesInstalled = False
            song_played = False # signals to perform a download
        else:
            iTunesInstalled = True
            song_played = iTunes.check_iTunes_for_song(iTunesPaths, autoDownload, speechRecogOn, pathToDirectory, command, mic=mic, r=r)

        if song_played == GlobalVariables.quit_string: # return to home
            return

        if prog_vers == GlobalVariables.alb_mode_string:
            trackProperties = songs_in_album_props[i]
            searchForSong = album_artist_list[i] + ' ' + searchForSong
        # secret command for syncing with gDrive files.  Special feature!
        elif searchFor == '1=1':
            Editor.syncWithGDrive(gDriveFolderPath=musicPlayerSettings["gDrive"]["gDriveFolderPath"],
                                  iTunesAutoAddFolderPath=iTunesPaths['autoAdd'])
            break

        elif song_played == False: # if song_played is True, suggests user played song or wants to skip iteration, thus perform download
            if speechRecogOn == True:
                responseText = SpeechAnalysis.main(mic,
                                                    r,
                                                    talking=True,
                                                    OS=sys.platform,
                                                    string_to_say="File not found. Would you like to download %s" %(tools.stripFileForSpeech(searchFor)),
                                                    file_to_play=os.path.join(pathToDirectory, 'speechPrompts', 'wouldyouDL.m4a'),
                                                    pathToDirectory=pathToDirectory,
                                                    expected=['yes', 'no'])
                if 'yes' in responseText: # check if user wants to download or not
                    computer.speak(sys.platform, 'Downloading.', os.path.join(pathToDirectory, 'speechPrompts', 'downloading.m4a'))
                    autoDownload=True # perform autodownload for that songs
                else:
                    return

            trackProperties = iTunesSearch.parseItunesSearchApi(searchVariable=searchForSong,
                                                                limit=10, entity='song',
                                                                autoDownload=autoDownload,
                                                                requiredJsonKeys=requiredJsonSongKeys,
                                                                searchOrLookup=True
                                                                )
            if trackProperties == GlobalVariables.quit_string: # return to home entry
                return
            elif trackProperties != None: # check to ensure that properties aree selected
                searchForSong = "%s %s" % (trackProperties['artistName'], trackProperties['trackName'])

        if song_played == False: # run for either album or regualar song download
            run_download(microPhone=mic,
                         recognizer=r,
                         iTunesInstalled=iTunesInstalled,
                         searchFor=searchForSong,
                         autoDownload=autoDownload,
                         pathToDirectory=pathToDirectory,
                         iTunesPaths=iTunesPaths,
                         speechRecogOn=speechRecogOn,
                         debugMode=debugMode,
                         trackProperties=trackProperties,
                         musicPlayerSettings = musicPlayerSettings)

        print('=----------Done Cycle--------=')

# 'auto' argv will get first video.  Manual will allow user to select video.. default behaviour
# pass argv to youtubeSongDownload
"""
Main function that runs to launch the music player program
args: command line args, speech recognizer object, microphone object, iTunes paths to auto add folder and songs dict,
      speech recognizer mode on or not, debug mode on or not
Returns: None
"""
def main(argv='', r=None, mic=None, pathToItunesAutoAdd={}, speechRecogOn=False, debugMode = False):
    autoDownload = False
    searchList = []
    requiredJsonSongKeys = ['trackName',
                          'artistName',
                          'collectionName',
                          'artworkUrl100',
                          'primaryGenreName',
                          'trackNumber',
                          'trackCount']
    requiredJsonAlbumKeys = ['artistName', 'collectionName', 'trackCount', 'collectionId']
    album_artist_list=[]
    songs_in_album_props=[]

    song_played = False # determines if song has been played by itunes.
    prog_vers = ''
    command=''
    autoDownload = False
    speechRecogOn = False
    debugMode = False
    listOfModes = ['auto','voice','debug', 'select', 'voice debug', 'auto debug']


    # get the obsolute file path for the machine running the script
    pathToDirectory= os.path.dirname(os.path.realpath(__file__))
    localDumpFolder = os.path.join(pathToDirectory, 'dump')
    pathToSettings = os.path.join(pathToDirectory, 'settings.json')

    # initialize settings
    if not os.path.exists(pathToSettings):
        with open(pathToSettings, 'w') as f:
            initialized_settings = {
                                    "gDrive" : {"gDriveFolderPath": "", "folder_id" : ""}, 
                                    "iTunes" : {"userWantsiTunes" : "y",
                                                "iTunesAutoPath"  : "",
                                                "iTunesSongsPath" : "",
                                                "iTunesBasePath"  : ""}
                                    }
            initialized_settings["gDrive"] = gDrive.get_info()
            json.dump(initialized_settings, f)

    with open(pathToSettings, 'r') as in_file:
        musicPlayerSettings = json.loads(in_file.read())

    # initialize dump directory
    if not os.path.exists(localDumpFolder):
        os.makedirs(localDumpFolder)

    restart_required = False
    chrome_needed_instlld = False 
    ffm_needed_instlld = False
    # initialize chromedriver
    if not updates.chromedr_installed():
        print("You don't have chromedriver installed. Let me take care of that for you :)")
        chromedriver_folder = updates.chromeDriver(GlobalVariables.chromedriver_update_url, modify_path=True)
        chrome_needed_instlld = True
    
    # initialize ffmpeg
    if not updates.ffmpeg_installed():
        print("You don't have ffmpeg installed. Let me take care of that as well I guess..")
        ffmpeg_folder = updates.ffmpeg("https://ffmpeg.zeranoe.com/builds/", modify_path=True)
        ffm_needed_instlld = True 
    
    if chrome_needed_instlld or ffm_needed_instlld:
        if sys.platform == 'win32':
            updates.modify_path(chrome_needed_instlld, chromedriver_folder, ffm_needed_instlld, ffmpeg_folder)

        print("Please restart cmd now for the software changes to take effect.")
        return

    # check for running version
    if len(argv) > 1:
        argv_noPath = argv.pop(0)
        autoDownload, speechRecogOn, debugMode = feature.determine_mode(argv)
    # initialize for speechRecogOn
    if speechRecogOn == True: # TODO CHANGE BACK
        mic = sr.Microphone()
        r = sr.Recognizer()

    # determine which OS we are operating on.  Work with that OS to set
    operatingSystem = namePlates(autoDownload, speechRecogOn, debugMode, sys.platform)

    continueGettingSongs = 'yes' # initialize to yes in order to trigger idle listening
    searchFor = ''

    while continueGettingSongs != 'no' :
        # initialize searchList to empty each iteration
        searchList = []

        if speechRecogOn == False:
            searchFor = input("Enter song(s) [song1; song2], 'instr' for instructions, 'set' for settings, 'alb' for albums: ")
            if searchFor in listOfModes: # will be used to determine if mode chaneg has been selected
                command = searchFor

            if searchFor == 'set':
                prog_vers = 'set'
                feature.editSettings(pathToSettings=pathToSettings)
            elif searchFor == 'instr':
                prog_vers = 'instr'
                feature.view_instructions(os.path.join(pathToDirectory, 'Instructions.txt'))
            elif searchFor == GlobalVariables.alb_mode_string:
                prog_vers = GlobalVariables.alb_mode_string
                album_user_input = input("Enter artist and album name you wish to download. Type 406 to cancel: ")
                if album_user_input == GlobalVariables.quit_string:
                    searchList = album_user_input # will quit out.
                else:
                    searchList, album_artist_list, songs_in_album_props = iTunesSearch.launch_album_mode(artist_album_string=album_user_input,
                                                                            requiredJsonSongKeys=requiredJsonSongKeys,requiredJsonAlbumKeys=requiredJsonAlbumKeys,
                                                                            autoDownload=False, prog_vers=prog_vers)

            else:
                searchList = searchFor.split('; ')
                prog_vers = ''

        else: # Speech recognition edition
            if continueGettingSongs == "yes": # idly listen if user say's yes otherwise use searchList from end of loop
                while True:
                    speechResponse = SpeechAnalysis.main(mic, r, talking=False, phrase_time_limit=4)
                    command, searchList = computer.interpret_command(speechResponse, only_command=False)

                    if command == 'quit':
                        return
                    if command != None: # break loop if successful transcription occurs
                        break


            else: # get the next songs from previous iteration of speech
                searchList = list(continueGettingSongs)

        if command in listOfModes: # determine which version to be in.
            command = command.split(' ')
            autoDownload, speechRecogOn, debugMode = feature.determine_mode(command)
            operatingSystem = namePlates(autoDownload, speechRecogOn, debugMode, sys.platform)
            if speechRecogOn == True: # declare microphone and recognizer instance
                mic = sr.Microphone()
                r = sr.Recognizer()
            continue # return to top of loop.

        if searchList != GlobalVariables.quit_string: # if it is, skip whole song playing/searching process
            # Iterate the list of songs
            print(command, searchList)
            run_for_songs(mic=mic, r=r, searchList=searchList, autoDownload=autoDownload,
                            pathToDirectory=pathToDirectory, speechRecogOn=speechRecogOn, debugMode=debugMode,command=command,
                            musicPlayerSettings=musicPlayerSettings, prog_vers=prog_vers, operatingSystem=operatingSystem, searchFor=searchFor,
                            requiredJsonSongKeys=requiredJsonSongKeys, album_artist_list=album_artist_list,
                            songs_in_album_props=songs_in_album_props)

        if speechRecogOn == False:
            continueGettingSongs = input('Want to go again (yes/no): ')

        if speechRecogOn == True:
            nextSongs = [] # initialize to empty before ech speech read
            nextSongs = SpeechAnalysis.main(mic,
                                              r,
                                              talking=True,
                                              OS=operatingSystem,
                                              string_to_say='Say another command or no to quit.',
                                              file_to_play=os.path.join(pathToDirectory, 'speechPrompts', 'anotherone.m4a'),
                                              pathToDirectory=pathToDirectory,
                                              phrase_time_limit=4)
            new_command, continueGettingSongs = computer.interpret_command(nextSongs, only_command=False)
            command = new_command # unpacking is weird. If i used command it would not update.
            if continueGettingSongs == None: # if no command is interpreted, return to idle mode
                computer.speak(sys.platform, string_to_say='No command given. Returning to idle.',
                              file_to_play=os.path.join(sys.path[0],'speechPrompts','noCommandReturnIdle.m4a'))
                continueGettingSongs = 'yes'
            elif continueGettingSongs[0] == 'no':
                break # quit

    # editor functionality goes here (from iTunesManipulator.Editor)
    print("\n================================")
    print("=--------Have a fine day-------=")
    print("================================")
    if speechRecogOn == True and operatingSystem=='darwin':
        computer.speak(operatingSystem, 'Goodbye.')


if __name__=="__main__":
    main(sys.argv)
