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
def test():
    print(sys.path)

def getYoutubeInfoFromDataBase(searchQuery={'search_query':''}, songName=''):
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

# integerVideoId defaults to 0, but can be used in autodownload recusively to remove the bad link to song.
def youtubeSongDownload(youtubePageResponse, autoDownload=False, pathToDumpFolder='', pathToSettings='', debugMode=False, counter=0, integerVideoId=None):
    # array of tuples for storing (title, url)
    videoUrls = []

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
    browser.save_screenshot('/Users/christianboin/Desktop/headless.png')
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
        integerVideoId = counter

    else:
        if integerVideoId == None:
            integerVideoId = int(input("Select the song you want by entering the number beside it. [%d to %d].. '404' to search again: " % (0, len(videoUrls)-1)))
        else:
            integerVideoId = int(input("Select the song you want by entering the number beside it. Not [%d].. '404' to search again: " % (integerVideoId)))
        ## Error handle for function.. check None type in Main
        if integerVideoId == 404:
            responseObject['success'] = False
            responseObject['error'] = '404'
            return responseObject

        # error handling for url selection.. check for None type removed link from line 67
        while integerVideoId not in range(0, len(videoUrls)) or videoUrls[integerVideoId][1] == None:
            integerVideoId = int(input("Try Again (Not [%s]) " % (integerVideoId)))

    videoSelection = videoUrls[integerVideoId][0]
    browser.get('https://ytmp3.cc/')
    formInput = browser.find_element_by_name('video')
    formInput.send_keys(videoUrls[integerVideoId][1])
    formInput.submit()
    print("Converting: %s" % (videoSelection))

    try:
        # ensure the javascript has time to run, when the id="Download" appears it is okay to close window.
        wait = WebDriverWait(browser, 10)
        # page fully loaded upon download id being present
        element = wait.until(EC.element_to_be_clickable((By.LINK_TEXT, 'Download')))

        pageText = BeautifulSoup(browser.page_source, 'html.parser')

        # tag a with attribute download='file.mp3' containt the downloadlink at href attr
        downloadTag = pageText.find('a', string="Download")
        downloadLink = downloadTag.get('href')

    except:
        print("!!-----Error------!!")
        print("Something went wrong on the youtubetomp3 website: ")
        print("This error is on their side.. either the conversion timed out or the file can't be converted on that site.")
        print("Returning to song search.. Please Try again")

        if counter >= 5:
            responseObject['success'] = False
            responseObject['error'] = 'youMP3fail'
            print("Tried 5 different downloads.. all failed. Quitting to final menu")
            return
        else:
            return youtubeSongDownload(youtubePageResponse, autoDownload, pathToDumpFolder, pathToSettings, debugMode, counter=counter+1, integerVideoId=integerVideoId)

    print("Downloading from: ", downloadLink)

    browser.close()

    # must strip the illegal characters from the videoTitle for saving to work smoothly
    print('Removing any illegal characters in filename.')
    videoSelection = removeIllegalCharacters(videoSelection)

    localSaveFileToPath = os.path.join(pathToDumpFolder, videoSelection + '.mp3')

    successOrFailureDownloading = dumpAndDownload(filepath=localSaveFileToPath,
                                            downloadLink=downloadLink,
                                            local_filename=videoSelection,
                                            counter=youTubeMP3_settings['downloads']['tryCount'],
                                            waitTime=youTubeMP3_settings['downloads']['retryTime'])

    if successOrFailureDownloading == 'success':
        print("Done. Playing.. " + videoSelection + ".mp3" + " Now. Enjoy")
        print("Located currently at: ", os.path.join(localSaveFileToPath))

        responseObject['error'] = None
        responseObject['success'] = True
        responseObject['songPath'] = os.path.join(localSaveFileToPath)
        return responseObject

    if successOrFailureDownloading == 'failure':
        print('I have failed downloading.. It took too many tries.')
        responseObject['success'] = False
        responseObject['error'] = 'dlFail'
        return responseObject

def removeIllegalCharacters(fileName):

    return fileName.replace('\\', '').replace('"', '').replace('/', '').replace('*', '').replace('?', '').replace('<', '').replace('>', '').replace('|', '').replace("'", '').replace(':', '')


def dumpAndDownload(filepath, downloadLink, local_filename, counter=0, waitTime=0):
    # check for content length.. reuired for progress bar
    chunk = 1
    chunk_size=1024
    download = 0
    success = 'success'
    failure = 'failure'

    getRequestResponse = requests.get(downloadLink, stream=True)
    file_size = getRequestResponse.headers.get('Content-Length')

    with open(filepath, 'wb') as fp:
        firstTime = time.time()

        if file_size == None:
            print('-------------------------')
            print("No file size.. so no progress bar.. Downloading")
            iter_content = getRequestResponse.iter_content(chunk_size=chunk_size)

        else:
            file_size = int(file_size)
            chunk = 1
            chunk_size=1024
            num_bars = int(file_size / chunk_size)
            iterable = getRequestResponse.iter_content(chunk_size=chunk_size)
            iter_content = tqdm.tqdm( # set iterable to progress Bar
                            iterable
                            , total= num_bars
                            , unit = 'KB'
                            , desc = local_filename
                            , leave = True # progressbar stays
                            , dynamic_ncols=True
                            )

        for chunk in  iter_content:
            fp.write(chunk)
            nextTime = time.time()

            # must close bar if this flag is checked. this way it prints properly
            if nextTime - firstTime > waitTime:
                progressBar.close()
                print('Slow download.. trying again.. took >%d seconds' % (nextTime - firstTime))

                if counter == 0:
                    print('Tried a few times.. but the downloads are slow.')
                    return failure

                else:
                    return dumpAndDownload(filepath=filepath,
                                        downloadLink=downloadLink,
                                        local_filename=local_filename,
                                        counter=counter-1,
                                        waitTime=waitTime)

    # should only get here if the download is successful
    return success
