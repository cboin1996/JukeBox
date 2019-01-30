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
import speech_recognition as sr
import SpeechRecognitionToText
import time

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


def youtubeSongDownload(youtubePageResponse, autoDownload=False, pathToDumpFolder=''):
    videoUrls = []

    responseObject = {
        'error' : '',
        'success' : False,
        'songPath' : None
    }

    # open youtube response with selenium to ensure javascript loads
    options = webdriver.ChromeOptions()
    # add options to make the output pretty, no browser show and no bs outputs
    options.add_argument('headless')
    options.add_argument('--disable-gpu')
    browser = webdriver.Chrome(options=options)
    # browser = webdriver.Safari()
    browser.get(youtubePageResponse.url)

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
            print(' %d - %s: %s' %(i, title, videoUrl))
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
        integerVideoId = int(input("Select the song you want by entering the number beside it. [%d to %d].. '404' to search again: " % (0, len(videoUrls)-1)))

        ## Error handle for function.. check None type in Main
        if integerVideoId == 404:
            responseObject['success'] = False
            responseObject['error'] = '404'
            return responseObject

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
    downloadTag = pageText.find('a', target='_blank')

    try:
        downloadLink = downloadTag.get('href')

    except:
        error = pageText.find('div', class_="alert alert-warning")
        print("Something went wrong on the youtubetomp3 website: ")

        print(error.contents)

        print("I swear this doesn't happen to me often.")
        print("Returning to song search.")
        responseObject['success'] = False
        responseObject['error'] = 'youMP3fail'
        return responseObject


    print("Downloading from: ", downloadLink)

    browser.close()

    # must strip the illegal characters from the videoTitle for saving to work smoothly
    print('Removing any illegal characters in filename.')
    videoSelection = removeIllegalCharacters(videoSelection)


    localSaveFileToPath = os.path.join(pathToDumpFolder, videoSelection + '.mp3')

    successOrFailureDownloading = dumpAndDownload(filepath=localSaveFileToPath,
                                            downloadLink=downloadLink,
                                            local_filename=videoSelection,
                                            counter=2,
                                            waitTime=15)

    if successOrFailureDownloading == 'success':
        print("Done. Playing.. " + videoSelection + ".mp3" + " Now. Enjoy")
        print("Located currently at: ", os.path.join(localSaveFileToPath))

        responseObject['error'] = 'None'
        responseObject['success'] = True
        responseObject['songPath'] = os.path.join(localSaveFileToPath)
        return responseObject

    if successOrFailureDownloading == 'failure':
        print('I have failed downloading.. It took too many tries.')
        responseObject['success'] = False
        responseObject['error'] = 'dlFail'
        return responseObject

def removeIllegalCharacters(fileName):

    return fileName.replace('\\', '').replace('"', '').replace('/', '').replace('*', '').replace('?', '').replace('<', '').replace('>', '').replace('|', '').replace("'", '')


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

            for chunk in getRequestResponse.iter_content(chunk_size=chunk_size):
                fp.write(chunk)
                nextTime = time.time()

                # # DEBUG check to verify this works.. its acting funny
                if nextTime - firstTime > waitTime:
                    print('Slow download.. trying again.. took >%d seconds' % (nextTime - firstTime))

                    if counter == 0:
                        return failure

                    else:
                        return dumpAndDownload(filepath=filepath,
                                            downloadLink=downloadLink,
                                            local_filename=local_filename,
                                            counter=counter-1,
                                            waitTime=waitTime)

        else:
            file_size = int(file_size)
            chunk = 1
            chunk_size=1024
            num_bars = int(file_size / chunk_size)
            iterable = getRequestResponse.iter_content(chunk_size=chunk_size)
            progressBar = tqdm.tqdm(
                            iterable
                            , total= num_bars
                            , unit = 'KB'
                            , desc = local_filename
                            , leave = True # progressbar stays
                            , dynamic_ncols=True
                            )

            for chunk in  progressBar:
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
