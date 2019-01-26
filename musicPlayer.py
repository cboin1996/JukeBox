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
import iTunesSearch

# Change log

# Cboin v 1.1 -- added iTunesSearch functionality and worked on excpetion handling w/ try catch / userinput

def youtubeSongDownload(songName, searchQuery={'search_query':''}, autoDownload=False, pathToDumpFolder=''):
    videoUrls = []
    # get absolute path to file so the script csan be executed from anywhr
    pathToDirectory= os.path.dirname(os.path.realpath(__file__))
    pathToDatabase = os.path.join(pathToDirectory,'BasicWebParser', 'database.json')

    with open(pathToDatabase, "r") as read_file:
        websiteData = json.load(read_file)

    searchQuery['search_query'] = songName
    #initialize the class to use Youtube as the website
    youtubeSession = Logins.WebLoginandParse(websiteData, 'Youtube')

    # perform search of youtube...
    response = youtubeSession.enterSearchForm(youtubeSession.urls['homePage'], youtubeSession.urls['serviceSearch'], searchQuery)

    # open youtube response with selenium to ensure javascript loads
    options = webdriver.ChromeOptions()
    # add options to make the output pretty, no browser show and no bs outputs
    options.add_argument('headless')
    options.add_argument('--disable-gpu')
    browser = webdriver.Chrome(options=options)
    # browser = webdriver.Safari()
    browser.get(response.url)

    pageText = BeautifulSoup(browser.page_source, 'html.parser')

    # grab the list of video titles from the searched page
    print("Found these videos: ")
    i = 0
    for videotitle in pageText.find_all(id='video-title'):
        if videotitle.get('href') != None:
            videoUrl = 'https://www.youtube.com' + videotitle.get('href')
            title = videotitle.get('title')
            videoUrls.append((title, videoUrl))
            # prints the title of video pretilly
            print('%d - %s: %s' %(i, title, videoUrl))
            i += 1

    # append the watch url to the youtubetomp3 website and get with selenium so javascript loads
    # urls stored as list of tuples
    # check for command line argv -- autoDownload
    # if autoDownload is on, grab first URL. Else, user selects...
    if autoDownload == True:
        videoSelection = videoUrls[0][0]
        browser.get('https://www.easy-youtube-mp3.com/convert.php?v='+videoUrls[0][1])
        print("Converting: %s" % (videoSelection))

    else:
        integerVideoId = int(input("Select the song you want by entering the number beside it. [%d to %d] " % (0, len(videoUrls)-1)))

        # error handling for url selection
        while integerVideoId not in range(0, len(videoUrls)):
            integerVideoId = int(input("Try Again.. [%d to %d] " % (0, len(videoUrls)-1)))

        videoSelection = videoUrls[integerVideoId][0]
        browser.get('https://www.easy-youtube-mp3.com/convert.php?v='+videoUrls[integerVideoId][1])
        print("Converting: %s" % (videoSelection))

    # ensure the javascript has time to run, when the id="Download" appears it is okay to close window.
    wait = WebDriverWait(browser, 10)
    # page fully loaded upon download id being present
    element = wait.until(EC.presence_of_element_located((By.ID, 'Download')))

    pageText = BeautifulSoup(browser.page_source, 'html.parser')

    # tag a with attribute download='file.mp3' containt the downloadlink at href attr
    downloadTag = pageText.find('a', download='file.mp3')

    try:
        downloadLink = downloadTag.get('href')
    except:
        error = pageText.find('div', class_="alert alert-warning")
        print("Something went wrong on the youtubetomp3 website: ")

        print(error.contents)

        print("I swear this doesn't happen to me often.")
        print("Returning to song search.")

        return None


    print("Downloading from: ", downloadLink)

    browser.close()

    downloadResponse = requests.get(downloadLink, stream=True)

    # must strip the illegal characters from the videoTitle for saving to work smoothly
    videoSelection = removeIllegalCharacters(videoSelection)

    if downloadResponse.status_code == 200:
        localSaveFileToPath = os.path.join(pathToDumpFolder, videoSelection + '.mp3')
        dumpAndDownload(filepath=localSaveFileToPath, getRequestResponse=downloadResponse, local_filename=videoSelection)

    else:
        print("I just couldnt do it... something went wrong -- Response Code: ", downloadResponse)
        return None

    print("Done. Playing.. " + videoSelection + ".mp3" + " Now. Enjoy")
    print("Located currently at: ", os.path.join(localSaveFileToPath))

    return os.path.join(localSaveFileToPath)

def removeIllegalCharacters(fileName):
    print('Scanning and removing illegal characters from filename (if any)')

    return fileName.replace('\\', '').replace('"', '').replace('/', '').replace('*', '').replace('?', '').replace('<', '').replace('>', '').replace('|', '')


def dumpAndDownload(filepath, getRequestResponse, local_filename):
    # check for content length.. reuired for progress bar
    file_size = getRequestResponse.headers.get('Content-Length')

    with open(filepath, 'wb') as fp:
        if file_size == None:
            print("No file size.. so no progress bar.  Downloading.")
            fp.write(getRequestResponse.content)
        else:
            file_size = int(file_size)
            chunk = 1
            chunk_size=1024
            num_bars = int(file_size / chunk_size)
            for chunk in tqdm.tqdm(
                                    getRequestResponse.iter_content(chunk_size=chunk_size)
                                    , total= num_bars
                                    , unit = 'KB'
                                    , desc = local_filename
                                    , leave = True # progressbar stays
                                    , dynamic_ncols = True
                                    ):
                fp.write(chunk)

    return

def namePlates(argument, OS):
    print("================================")
    print("=-Welcome to the cBoin JukeBox-=")


    if argument == True:
        print("=------Automated Edition-------=")


    if argument == False:
        print("=--------Select Edition--------=")

    if OS == 'darwin':
        print("=---------For MAC OS X---------=")

    if OS == 'win32':
        print("=---------For Windows----------=")

    print("=------------V1.0--------------=")
    print("================================")

    return OS

def setItunesPaths(operatingSystem, iTunesPaths={'autoAdd':'', 'searchedSongResult':[]}, searchFor=''):
    iTunesPaths['searchedSongResult'] = []

    if operatingSystem == 'darwin':
        pathToItunesAutoAdd = os.path.join('/Users', '*', 'Music', 'iTunes', 'iTunes Media', 'Automatically Add to iTunes.localized')
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

    if operatingSystem == 'win32':
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

    return iTunesPaths

def iTunesLibSearch(songPaths, iTunesPaths={}, searchParameters=''):
    for songPath in songPaths:
        songNameSplit = songPath.split(os.sep)
        if searchParameters.lower() in songNameSplit[len(songNameSplit)-1].lower():
            iTunesPaths['searchedSongResult'].append(songPath)

    return iTunesPaths

# this function allows the module to be ran with or without itunes installed.
# if iTunes is not installed, the files are tagged and stored in dump folder.
def runMainWithOrWithoutItunes(iTunesInstalled=True, searchFor='', autoDownload=False, localDumpFolder='', iTunesPaths={}):

    if iTunesInstalled == True:

        if len(iTunesPaths['searchedSongResult']) == 0:
            print("File not found in iTunes Library.. Getting From Youtube")

        else:

            # get the first item of the songs returned from the list of song paths matching
            # plays song immediatly, so return after this executes
            print("Here are song(s) in your library matching your search: ")
            i = 0
            for songPath in iTunesPaths['searchedSongResult']:
                songName = songPath.split(os.sep)
                print('%d - %s' % (i, songName[len(songName)-1]))
                i += 1

            songSelection = int(input("Which one do you want to hear? Type '404' to search youtube instead. "))

            # play the song only if they want, otherwise continute with program.
            if songSelection != 404:
                while songSelection not in range(0, len(iTunesPaths['searchedSongResult'])):
                    songSelection = int(input('Invalid Input. Try Again'))

                p = vlc.MediaPlayer(iTunesPaths['searchedSongResult'][songSelection])
                p.play()
                userInput = input("Hit Enter to stop playing... ")
                p.stop()
                return

    songPath = youtubeSongDownload(songName=searchFor, autoDownload=autoDownload, pathToDumpFolder=localDumpFolder)

    # None none type is good news.. continue as normal
    if songPath != None:
        p = vlc.MediaPlayer(songPath)
        p.play()

        trackProperties = iTunesSearch.parseItunesSearchApi(searchVariable=searchFor, limit=10, entity='song')

        # parseItunesSearchApi() throws None return type if the user selects no properties
        if trackProperties != None:
            properSongName = iTunesSearch.mp3ID3Tagger(mp3Path=songPath, dictionaryOfTags=trackProperties)

        else:
            print('Skipping tagging process (No itunes properties selected)')

        if iTunesInstalled == True:
            userInput = input("Type 's' to save to itunes, anything else to save locally to 'dump' folder. ")
            if userInput == 's':
                # dont know if i want this extra input
                # input("Your file is ready to be moved.. just hit enter to stop playing.")
                p.stop()
                shutil.move(songPath, iTunesPaths['autoAdd'])
                print("Moved your file to iTunes.")

        else:
            input("Local File is ready. Hit enter to stop playing.")
            p.stop()

# 'auto' argv will get first video.  Manual will allow user to select video.. default behaviour
# pass argv to youtubeSongDownload
def main(argv, pathToItunesAutoAdd={}):
    # get the obsolute file path for the machine running the script
    pathToDirectory= os.path.dirname(os.path.realpath(__file__))
    localDumpFolder = os.path.join(pathToDirectory, 'dump')

    #initialize dump directory
    if not os.path.exists(localDumpFolder):
        os.makedirs(localDumpFolder)

    # check for running version
    if len(argv) > 1:
        if argv[1] == 'auto':
            autoDownload = True
    else:
        autoDownload = False

    # determine which OS we are operating on.  Work with that OS to set
    operatingSystem = namePlates(autoDownload, sys.platform)

    continuePlaying = ''

    while continuePlaying != 'no':
        searchFor = input("Enter song: ")
        iTunesPaths = setItunesPaths(operatingSystem, searchFor=searchFor)
        # '*.*' means anyfilename, anyfiletype
        # /*/* gets through artist, then album or itunes folder structure
        if iTunesPaths == None:
            runMainWithOrWithoutItunes(iTunesInstalled=False, searchFor=searchFor, autoDownload=autoDownload, localDumpFolder=localDumpFolder, iTunesPaths=iTunesPaths)

        else:
            runMainWithOrWithoutItunes(iTunesInstalled=True, searchFor=searchFor, autoDownload=autoDownload, localDumpFolder=localDumpFolder, iTunesPaths=iTunesPaths)

        continuePlaying = input('Want to go again (yes/no): ')

    print("================================")
    print("=========Have a fine day========")
    print("================================")


if __name__=="__main__":
    main(sys.argv)
