import requests
from bs4 import BeautifulSoup
import re
from requests_html import HTMLSession
import tqdm
import os, shutil, stat, sys
import zipfile
import tarfile 
def getUrlForOS(urlList, OS):
    chromeDriverStorageLink = 'https://chromedriver.storage.googleapis.com'
    if OS == 'darwin':
        stringToQueryFor = 'mac64.zip'
        OSName = 'MacOS'
    elif OS == "win32":
        stringToQueryFor = 'win'
        OSName = 'Windows'
    else:
        stringToQueryFor = 'lin'
        OSName = 'Linux'
    for url in urlList:
        if stringToQueryFor in url:
            downloadLink = chromeDriverStorageLink+url
            print('Built your download link at: %s for %s' % (downloadLink, OSName))
    return downloadLink

def download(downloadResponse, chunk_size, filePath, pBarDescription):
    file_size = downloadResponse.headers.get('Content-Length')
    with open(filePath, 'wb') as fp:
        if file_size == 0:
            print("No file size, header downloading without progress bar.")
            for chunk in downloadResponse.iter_content(chunk_size=chunk_size):
                fp.write(chunk)

        else:
            file_size = int(file_size)
            chunk = 1
            num_bars = int(file_size / chunk_size)
            iterable = downloadResponse.iter_content(chunk_size=chunk_size)
            progressBar = tqdm.tqdm(
                            iterable,
                            total= num_bars,
                            unit = 'KB',
                            desc = pBarDescription,
                            leave = True,
                            dynamic_ncols=True
                            )
            for chunk in  progressBar:
                fp.write(chunk)

def update(response, driverPath, operatingSys, driver_folder=None, vers=None, modify_path=False):
    """""
    Unzips packages downloaded into desired folder and updates path if on windows 
    params: reponse: 
    """
    
    # check if the driver exists and remove old version
    if os.path.exists(driverPath):
        os.remove(driverPath)

    # download new version
    downloadPath = driverPath+'.zip'
    download(response, 10, downloadPath, f'{vers} - {operatingSys}')
    with zipfile.ZipFile(downloadPath, 'r') as zip_ref:
        zip_ref.extractall(driver_folder)

        if operatingSys == 'darwin' and vers=='ffmpeg':
            shutil.move(os.path.join(driverPath, 'bin', 'ffmpeg'), driver_folder) # move ffmpeg into the usr/local/bin/ folder
            shutil.rmtree(driverPath) # remove the big ffmpeg folder downloaded
            driverPath = driver_folder + "ffmpeg" # update driver path so that chmod may be ran
            
    os.remove(downloadPath)

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
        

def chromeDriver(url, modify_path=False):
    retryCount = 0
    session = HTMLSession()
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    # latest stable release found with stable in span tag.  Get the hyperlink nextTime
    # and then open up that link to perform download.
    tag = soup.find('span', string=re.compile('stable'))
    download_link = tag.findNext('a').get('href')
    print("Gathered the latest download version at the link: ", download_link)
    response = session.get(download_link)
    response.html.render(timeout=0, sleep=2)

    while len(response.html.links) == 0 and retryCount <= 3:
        print("Could not find link.. Retrying")
        response = session.get(download_link)
        response.html.render(timeout=0, sleep=2)
        retryCount += 1

    if len(response.html.links) != 0:
        urlList = response.html.links
        downloadLink = getUrlForOS(urlList, sys.platform)
        response = requests.get(downloadLink)
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