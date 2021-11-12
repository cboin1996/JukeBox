import requests
from bs4 import BeautifulSoup
import re
from requests_html import HTMLSession
import tqdm
import os, shutil, stat, sys
import zipfile
import tarfile 
import globalvariables

def check_for_updates() -> bool:
    """Check for updates. 

    Returns:
        bool: true if a restart is required
    """
    chrome_needed_instlld = False
    ffm_needed_instlld = False
    chromedriver_folder = ""
    ffmpeg_folder = ""
    # initialize chromedriver
    if not chromedr_installed():
        print("You don't have chromedriver installed. Let me take care of that for you :)")
        chromedriver_folder = chrome_driver(globalvariables.chromedriver_update_url, modify_path=True)
        chrome_needed_instlld = True

    # initialize ffmpeg
    if not ffmpeg_installed():
        print("You don't have ffmpeg installed. Let me take care of that as well I guess..")
        ffmpeg_folder = ffmpeg("https://ffmpeg.zeranoe.com/builds/", modify_path=True)
        ffm_needed_instlld = True

    if chrome_needed_instlld or ffm_needed_instlld:
        if sys.platform == 'win32':
            modify_path(chrome_needed_instlld, chromedriver_folder, ffm_needed_instlld, ffmpeg_folder)
            print("Please restart cmd now for the software changes to take effect.")
            return True
    
    return False

def get_url_for_os(url_list, operating_system):
    chrome_driver_storage_url = 'https://chromedriver.storage.googleapis.com'
    if operating_system == 'darwin':
        query_string = 'mac64.zip'
        operating_system_str = 'MacOS'
    elif operating_system == "win32":
        query_string = 'win'
        operating_system_str = 'Windows'
    else:
        query_string = 'lin'
        operating_system_str = 'Linux'
    for url in url_list:
        if query_string in url:
            chrome_driver_download_url = chrome_driver_storage_url+url
            print('Built your download link at: %s for %s' % (chrome_driver_download_url, operating_system_str))
    return chrome_driver_download_url

def download(download_response, chunk_size, file_path, progress_bar_description):
    file_size = download_response.headers.get('Content-Length')
    with open(file_path, 'wb') as fp:
        if file_size == 0:
            print("No file size, header downloading without progress bar.")
            for chunk in download_response.iter_content(chunk_size=chunk_size):
                fp.write(chunk)

        else:
            file_size = int(file_size)
            chunk = 1
            num_bars = int(file_size / chunk_size)
            iterable = download_response.iter_content(chunk_size=chunk_size)
            progress_bar = tqdm.tqdm(
                            iterable,
                            total= num_bars,
                            unit = 'KB',
                            desc = progress_bar_description,
                            leave = True,
                            dynamic_ncols=True
                            )
            for chunk in  progress_bar:
                fp.write(chunk)

def update(response, driver_path, operating_system, driver_folder=None, vers=None, modify_path=False):
    """""
    Unzips packages downloaded into desired folder and updates path if on windows 
    params: reponse: 
    """
    
    # check if the driver exists and remove old version
    if os.path.exists(driver_path):
        os.remove(driver_path)

    # download new version
    download_path = driver_path+'.zip'
    download(response, 10, download_path, f'{vers} - {operating_system}')
    with zipfile.ZipFile(download_path, 'r') as zip_ref:
        zip_ref.extractall(driver_folder)

        if operating_system == 'darwin' and vers=='ffmpeg':
            shutil.move(os.path.join(driver_path, 'bin', 'ffmpeg'), driver_folder) # move ffmpeg into the usr/local/bin/ folder
            shutil.rmtree(driver_path) # remove the big ffmpeg folder downloaded
            driver_path = driver_folder + "ffmpeg" # update driver path so that chmod may be ran
            
    os.remove(download_path)

    if sys.platform != 'win32':
        os.chmod(driverPath, stat.S_IXUSR)

def chromedr_installed():
    if sys.platform == 'win32':
        chromedr_exists = True if os.path.exists(os.path.join('C:', os.sep, 'webdrivers', 'chromedriver.exe')) else False 
    
    elif sys.platform == 'darwin':
        chromedr_exists = True if os.path.exists('/usr/local/bin/chromedriver') else False
    
    else:
        chromedr_exists = True if os.path.exists('/usr/bin/chromedriver') else False
    
    return chromedr_exists
        

def chrome_driver(url, modify_path=False):
    retry_count = 0
    session = HTMLSession()
    response = session.get(url)
    response.html.render(timeout=0, sleep=2)
    soup = BeautifulSoup(response.text, 'html.parser')

    # latest stable release found with stable in span tag.  Get the hyperlink nextTime
    # and then open up that link to perform download.
    tag = soup.find(text=lambda t: "stable" in t)
    download_link = tag.findNext('a').get('href')
    print("Gathered the latest download version at the link: ", download_link)
    response = session.get(download_link)
    response.html.render(timeout=0, sleep=2)

    while len(response.html.links) == 0 and retry_count <= 3:
        print("Could not find link.. Retrying")
        response = session.get(download_link)
        response.html.render(timeout=0, sleep=2)
        retry_count += 1

    if len(response.html.links) != 0:
        url_list = response.html.links
        download_link = get_url_for_os(url_list, sys.platform)
        response = requests.get(download_link)
        if sys.platform == 'darwin':
            driverPath = '/usr/local/bin/chromedriver'
            driver_folder = '/usr/local/bin/'
            update(response, driverPath, sys.platform, driver_folder, vers='chromedriver')
        elif sys.platform == 'win32':
            driver_folder = os.path.join('C:', os.sep, 'webdrivers')
            driverPath = os.path.join(driver_folder, 'chromedriver')

            if not os.path.exists(driver_folder):
                os.mkdir(driver_folder)

            update(response, driverPath, sys.platform, driver_folder, vers='chromedriver', modify_path=modify_path)
        else:
            driverPath = '/usr/bin/chromedriver'
            update(response, driverPath, sys.platform, vers='chromedriver')
        
        return driver_folder

    else:
        print("Failed to update.  Contact Christian for help.")
        return 0

def ffmpeg_installed():
    if sys.platform == 'win32':
        ffmpeg_root_path = os.path.join("C:", os.sep, "ffmpeg", "ffmpeg-20200424-a501947-win64-static", "bin", "ffmpeg.exe")
        ffmpeg_exists = True if os.path.exists(ffmpeg_root_path) else False
    else: # TODO: Implement in MAC/Linux
        ffmpeg_exists = True if os.path.exists("/usr/local/bin/ffmpeg") else False

    return ffmpeg_exists

def ffmpeg(url, modify_path=False):
    if sys.platform == 'win32':
        ffmpeg_root_path = os.path.join("C:", os.sep, 'ffmpeg')
        if not os.path.exists(ffmpeg_root_path):
            os.mkdir(ffmpeg_root_path)
        ffmpeg_location = os.path.join(ffmpeg_root_path, "ffmpeg-20200424-a501947-win64-static")
        download_link = url + "/win64/static/ffmpeg-20200424-a501947-win64-static.zip"
        path_to_binary = os.path.join(ffmpeg_location, "bin")
    
    elif sys.platform ==  'darwin':
        download_link = url + "/macos64/static/ffmpeg-20200424-a501947-macos64-static.zip"
        ffmpeg_location = "/usr/local/bin/ffmpeg-20200424-a501947-macos64-static"
        path_to_binary = "/usr/local/bin/"
        ffmpeg_root_path = path_to_binary

    print(f"Using ffmpeg download link at {download_link}")

    download_response = requests.get(download_link, stream=True)

    update(download_response, ffmpeg_location, sys.platform, ffmpeg_root_path, vers='ffmpeg', 
           modify_path=modify_path)
    return path_to_binary

def modify_path(chrome_instlld, chromedriver_folder, ffm_instlld, ffmpeg_folder):
    """
    Used to set windows path according to ffmpeg and chrome driver install
    Needs to be run in one setx operation, as otherwise the cmd would need relaunching between the setx -M operations.
    params: chrome_installd 
            chrome_driver_folder
            ffm_instlld
            ffmpeg_driver_folder
    returns: None
    """
    if chrome_instlld and ffm_instlld:
        paths_to_add = f"{chromedriver_folder};{ffmpeg_folder}"
    elif chrome_instlld and not ffm_instlld:
        paths_to_add = f"{chromedriver_folder}"
    elif ffm_instlld and not chrome_instlld:
        paths_to_add = f"{ffmpeg_folder}"
    os.system(f'setx /M path "%path%;{paths_to_add}"')

if __name__=="__main__":
    ffmpeg("https://www.ffmpeg.org/download.html")
    # chromeDriver("https://chromedriver.chromium.org")