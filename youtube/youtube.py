import requests
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

from webparse import logins, updates
from itunes import search
import speech_recognition as sr
import speechanalysis
from features import tools
import globalvariables

import time
import youtube_dl
from youtube_dl.utils import DownloadError, UnavailableVideoError, ExtractorError



def get_youtube_info_from_database(search_query={'search_query':''}, song_name=''):
    """
    Gathers youtube html tags information from json database
    args: search dict with youtubes query html tag, song name to search youtube for
    Returns: response from youtube search
    """
    # get absolute path to file so the script csan be executed from anywhr
    base_dir= os.path.dirname(os.path.realpath(__file__))
    path_to_database = os.path.join(base_dir, '..', 'webparse', 'database.json')

    with open(path_to_database, "r") as read_file:
        website_data = json.load(read_file)

    search_query['search_query'] = song_name
    #initialize the class to use Youtube as the website
    youtube_session = logins.WebLoginandParse(website_data, 'Youtube')

    # perform search of youtube...
    return youtube_session.enter_search_form(youtube_session.urls['homePage'], youtube_session.urls['serviceSearch'], search_query)

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
    if d['status'] == 'error':
        print("Error occured during download.")
        success_downloading = False

# integerVideoId defaults to 0, but can be used in autodownload recusively to remove the bad link to song.

def download_song_from_youtube(youtube_page_response, auto_download_enabled=False, path_to_dump_folder="", path_to_settings="", debug_mode=False, counter=0, integer_video_id=None,
                                file_format=""):
    """
    Walks user through song selection and downloading process
    args: 
        youtube_page_response: Youtube web page response
        auto_download_enabled: autodownload on or off
        path_to_dump_folder: path to the dump folder for songs
        path_to_settings: path to settings folder debug mode on or off
        counter: counter for download retries
        integer_video_id: integer representing a youtube video to try converting
        file_format: the format of file to use.
    Returns: response object with error status, success boolean and song path
    """
    # options for youtube_dl program
    ydl_opts = {
        'format': 'bestaudio/best',
        'cachedir': False,
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': file_format,
            'preferredquality': '192',
        }],
        'nocheckcertificate': True,
        'logger': MyLogger(),
        'progress_hooks': [my_hook],
    }

    response_object = {
        'error' : None,
        'success' : False,
        'songPath' : None
    }
    with open(path_to_settings, "r") as read_file:
        music_player_settings = json.load(read_file)

    integer_video_id, video_urls, browser, response_object = select_song_from_youtube_response(youtube_page_response, integer_video_id, auto_download_enabled, counter, debug_mode)

    try:
    # must strip the illegal characters from the videoTitle for saving to work smoothly
        video_selection = video_urls[integer_video_id][0]
        print('Removing any illegal characters in filename.')
        video_selection = remove_illegal_characters(video_selection)
        print("Converting: %s from link %s" % (video_selection, video_urls[integer_video_id][1]))
        local_save_file_path = os.path.join(path_to_dump_folder, video_selection + "." + file_format)
        songname_for_yt_dl = os.path.join(path_to_dump_folder, video_selection)
        ydl_opts['outtmpl'] = songname_for_yt_dl + ".%(ext)s"

        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            ydl.download([video_urls[integer_video_id][1]])

        success_downloading = True

    except DownloadError:
        print("Attempting to update.. ")
        # try to update the users youtube-dl installation.
        if sys.platform == 'win32':
            os.system('pip install --upgrade youtube-dl')
        elif sys.platform == 'darwin':
            os.system('pip3 install --upgrade youtube-dl')
        elif sys.platform == 'linux':
            os.system('pip install --upgrade youtube-dl')
        
        response_object['success'] = False
        response_object['error'] = 'had_to_update'
        return response_object
        
    except Exception:
        print("!!-----Error------!!")
        print("Something went wrong with youtube-dl: ")
        print("Contact Christian for this one.")
        print("Returning to song search.. Please Try again")
        success_downloading = False
        if counter >= 5:
            response_object['success'] = False
            response_object['error'] = 'youMP3fail'
            print("Tried 5 different downloads.. all failed. Quitting to final menu")
            return response_object
        else:
            return download_song_from_youtube(youtube_page_response, auto_download_enabled, path_to_dump_folder,
                                        path_to_settings, debug_mode, counter=counter+1,
                                        integer_video_id=integer_video_id)

    browser.close()

    if success_downloading == True:
        print("Done. Playing.. " + video_selection + "." + file_format + " Now. Enjoy")
        print("Located currently at: ", os.path.join(local_save_file_path))

        response_object['error'] = None
        response_object['success'] = True
        response_object['songPath'] = os.path.join(local_save_file_path)
        return response_object

    else:
        print('I have failed downloading.. It took too many tries.')
        response_object['success'] = False
        response_object['error'] = 'dlFail'
        return response_object

def select_song_from_youtube_response(youtube_page_response, integer_video_id, auto_download_enabled, counter, debug_mode):
    response_object = {
        'error' : None,
        'success' : False,
        'songPath' : None
    }
    
    # array of tuples for storing (title, url)
    video_urls = []
    # open youtube response with selenium to ensure javascript loads
    # options = webdriver.ChromeOptions()
    options = Options()

    # add options to make the output pretty, no browser show and no bs outputs
    if not debug_mode:
        options.headless = True
    options.add_argument("--disable-extensions");
    options.add_argument('--disable-gpu')
    options.add_argument("--log-level=3")
    options.add_argument('--enable-blink-features=HTMLImports')
    
    if sys.platform == 'linux':
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')

    try:
        browser = webdriver.Chrome(options=options)
    except:
        print("ERROR>>>New version of ChromeDriver Required. Downloading")
        updates.chrome_driver(globalvariables.chromedriver_update_url, modify_path=False)
        browser = webdriver.Chrome(options=options)

    browser.get(youtube_page_response.url)

    page_text = BeautifulSoup(browser.page_source, 'html.parser')
    # browser.save_screenshot('/Users/christianboin/Desktop/headless.png') # uncomment to debug headless chrome
    # grab the list of video titles from the searched page
    print("Found these videos: ")
    i = 0
    for videotitle in page_text.find_all(id='video-title'):
        if videotitle.get('href') != None:
            video_url = "https://www.youtube.com" + videotitle.get('href')
            title = videotitle.get('title')
            if i == integer_video_id:
                print(' %d - Removed broken link here.' % (integer_video_id))
                video_urls.append(('Removed broken link here', None))
            else:
                video_urls.append((title, video_url))
                # prints the title of video pretilly
                print(' %d - %s: %s' %(i, title, video_url))
            i += 1
    # append the watch url to the youtubetomp3 website and get with selenium so javascript loads
    # urls stored as list of tuples
    # check for command line argv -- autoDownload
    if auto_download_enabled == True:
        integer_video_id = counter # from recursion

    else:
        if integer_video_id == None:
            prompt = "Select song by entering the number beside it. [%d to %d].. '404' (search again), '405' (cancel download): " % (0, len(video_urls)-1)
            integer_video_id = tools.format_input_to_int(prompt, 'save_no_prop', 0, len(video_urls)-1)
        else:
            prompt = "Select song by entering the number beside it. Not [%d].. '404' (search again), '405' (cancel download): " % (integer_video_id)
            integer_video_id = tools.format_input_to_int(prompt, 'save_no_prop', 0, len(video_urls)-1)

        if integer_video_id == 404:
            response_object['success'] = False
            response_object['error'] = '404'
            return response_object
        if integer_video_id == 405:
            response_object['success'] = False
            response_object['error'] = '405'
            return response_object

        # error handling for url selection.. check for None type removed link from line 67
        while video_urls[integer_video_id][1] == None:
            integer_video_id = int(input("Try Again (Not [%s]) " % (integer_video_id)))

    return integer_video_id, video_urls, browser, response_object

def remove_illegal_characters(filename):
    """
    Used for stripping file names of illegal characters used for saving
    args: the file's name to strip
    Returns: stipped file name
    """
    return filename.replace('\\', '').replace('"', '').replace('/', '').replace('*', '').replace('?', '').replace('<', '').replace('>', '').replace('|', '').replace("'", '').replace(':', '')
