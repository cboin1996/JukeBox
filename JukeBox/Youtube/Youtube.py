import requests
from BasicWebParser import Logins, updates
from bs4 import BeautifulSoup
import json
import vlc
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import glob
import shutil, os, tqdm, sys
from iTunesManipulator import iTunesSearch
import speech_recognition as sr
import SpeechAnalysis
import time
import youtube_dl
from Features import tools


def getYoutubeInfoFromDataBase(searchQuery={'search_query':''}, songName=''):
    """
    Gathers youtube html tags information from json database
    args: search dict with youtubes query html tag, song name to search youtube for
    Returns: response from youtube search
    """
    # get absolute path to file so the script csan be executed from anywhr
    pathToDirectory= os.path.dirname(os.path.realpath(__file__))
    pathToDatabase = os.path.join(pathToDirectory, '..', 'BasicWebParser', 'database.json')

    with open(pathToDatabase, "r") as read_file:
        websiteData = json.load(read_file)

    searchQuery['search_query'] = songName
    #initialize the class to use Youtube as the website
    youtubeSession = Logins.WebLoginandParse(websiteData, 'Youtube')

    # perform search of youtube...
    return youtubeSession.enterSearchForm(youtubeSession.urls['homePage'], youtubeSession.urls['serviceSearch'], searchQuery)

class MyLogger(object):
    """
    Used for setting up youtube_dl logging
    """
    def info(self, msg):
        print(msg)

    def debug(self, msg):
        pass

    def warning(self, msg):
        pass

    def error(self, msg):
        print(msg)


def my_hook(d):
    """
    Hook for youtube_dl
    param: d: download object from youtube_dl
    """
    if d['status'] == 'finished':
        sys.stdout.write('\n')
        print('Done downloading, now converting ...')
    if d['status'] == 'downloading':
        p = d['_percent_str']
        p = p.replace('%','')
        song_name = d['filename'].split(os.sep)[-1]
        sys.stdout.write(f"\rDownloading to file: {song_name}, {d['_percent_str']}, {d['_eta_str']}")
        sys.stdout.flush()

# integerVideoId defaults to 0, but can be used in autodownload recusively to remove the bad link to song.

def youtubeSongDownload(youtubePageResponse, autoDownload=False, pathToDumpFolder='', pathToSettings='', debugMode=False, counter=0, integerVideoId=None):
    """
    Walks user through song selection and downloading process
    args: Youtube web page response, autodownload on or off, path to the dump folder for songs
          path to settings folder, debug mode on or off, counter for download retries,
          integer representing a youtube video to try converting to mp3
    Returns: response object with error status, success boolean and song path
    """

    # array of tuples for storing (title, url)
    videoUrls = []
    # options for youtube_dl program
    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'nocheckcertificate': True,
        'logger': MyLogger(),
        'progress_hooks': [my_hook],
    }

    responseObject = {
        'error' : None,
        'success' : False,
        'songPath' : None
    }
    with open(pathToSettings, "r") as read_file:
        youTubeMP3_settings = json.load(read_file)

    # open youtube response with selenium to ensure javascript loads
    # options = webdriver.ChromeOptions()
    options = Options()

    # add options to make the output pretty, no browser show and no bs outputs
    if debugMode == False:
        options.headless = True
    options.add_argument("--disable-extensions");
    options.add_argument('--disable-gpu')
    options.add_argument("--log-level=3")
    options.add_argument('--enable-blink-features=HTMLImports')

    try:
        browser = webdriver.Chrome(options=options)
    except:
        print("ERROR>>>New version of ChromeDriver Required. Downloading")
        updates.chromeDriver("https://chromedriver.chromium.org")
        browser = webdriver.Chrome(options=options)

    browser.get(youtubePageResponse.url)

    pageText = BeautifulSoup(browser.page_source, 'html.parser')
    # browser.save_screenshot('/Users/christianboin/Desktop/headless.png') # uncomment to debug headless chrome
    # grab the list of video titles from the searched page
    print("Found these videos: ")
    i = 0
    for videotitle in pageText.find_all(id='video-title'):
        if videotitle.get('href') != None:
            videoUrl = 'https://www.youtube.com' + videotitle.get('href')
            title = videotitle.get('title')
            if i == integerVideoId:
                print(' %d - Removed broken link here.' % (integerVideoId))
                videoUrls.append(('Removed broken link here', None))
            else:
                videoUrls.append((title, videoUrl))
                # prints the title of video pretilly
                print(' %d - %s: %s' %(i, title, videoUrl))
            i += 1
    # append the watch url to the youtubetomp3 website and get with selenium so javascript loads
    # urls stored as list of tuples
    # check for command line argv -- autoDownload
    if autoDownload == True:
        integerVideoId = counter # from recursion

    else:

        if integerVideoId == None:
            prompt = "Select song by entering the number beside it. [%d to %d].. '404' (search again), '405' (cancel download): " % (0, len(videoUrls)-1)
            integerVideoId = tools.format_input_to_int(prompt, 'save_no_prop', 0, len(videoUrls)-1)
        else:
            prompt = "Select song by entering the number beside it. Not [%d].. '404' (search again), '405' (cancel download): " % (integerVideoId)
            integerVideoId = tools.format_input_to_int(prompt, 'save_no_prop', 0, len(videoUrls)-1)

        if integerVideoId == 404:
            responseObject['success'] = False
            responseObject['error'] = '404'
            return responseObject
        if integerVideoId == 405:
            responseObject['success'] = False
            responseObject['error'] = '405'
            return responseObject


        # error handling for url selection.. check for None type removed link from line 67
        while videoUrls[integerVideoId][1] == None:
            integerVideoId = int(input("Try Again (Not [%s]) " % (integerVideoId)))

    try:
    # must strip the illegal characters from the videoTitle for saving to work smoothly
        videoSelection = videoUrls[integerVideoId][0]
        print('Removing any illegal characters in filename.')
        videoSelection = removeIllegalCharacters(videoSelection)
        print("Converting: %s from link %s" % (videoSelection, videoUrls[integerVideoId][1]))
        localSaveFileToPath = os.path.join(pathToDumpFolder, videoSelection + '.mp3')
        ydl_opts['outtmpl'] = pathToDumpFolder + os.sep + "%(title)s.%(ext)s"
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            ydl.download([videoUrls[integerVideoId][1]])

        success_downloading = True if os.path.exists(localSaveFileToPath) else False

    except Exception as e:
        print(f"Exception is: {e}")
        print("!!-----Error------!!")
        print("Something went wrong with youtube-dl: ")
        print("Contact Christian for this one.")
        print("Returning to song search.. Please Try again")

        if counter >= 5:
            responseObject['success'] = False
            responseObject['error'] = 'youMP3fail'
            print("Tried 5 different downloads.. all failed. Quitting to final menu")
            return responseObject
        else:
            return youtubeSongDownload(youtubePageResponse, autoDownload, pathToDumpFolder,
                                        pathToSettings, debugMode, counter=counter+1,
                                        integerVideoId=integerVideoId)

    browser.close()

    if success_downloading == True:
        print("Done. Playing.. " + videoSelection + ".mp3" + " Now. Enjoy")
        print("Located currently at: ", os.path.join(localSaveFileToPath))

        responseObject['error'] = None
        responseObject['success'] = True
        responseObject['songPath'] = os.path.join(localSaveFileToPath)
        return responseObject

    else:
        print('I have failed downloading.. It took too many tries.')
        responseObject['success'] = False
        responseObject['error'] = 'dlFail'
        return responseObject


def removeIllegalCharacters(fileName):
    """
    Used for stripping file names of illegal characters used for saving
    args: the file's name to strip
    Returns: stipped file name
    """
    return fileName.replace('\\', '').replace('"', '').replace('/', '').replace('*', '').replace('?', '').replace('<', '').replace('>', '').replace('|', '').replace("'", '').replace(':', '')
