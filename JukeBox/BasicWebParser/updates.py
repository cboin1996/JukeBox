import requests
from bs4 import BeautifulSoup
import re
from requests_html import HTMLSession
import tqdm
import os, shutil, stat, sys
import zipfile

def getUrlForOS(urlList, OS):
    chromeDriverStorageLink = 'https://chromedriver.storage.googleapis.com'
    if OS == 'darwin':
        stringToQueryFor = 'mac'
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
            for chunk in response.iter_content(chunk_size=chunk_size):
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

def chromeDriver(url):
    retryCount = 0
    session = HTMLSession()
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    # latest stable release found with stable in span tag.  Get the hyperlink nextTime
    # and then open up that link to perform download.
    tag = soup.find("span", string=re.compile('stable'))
    downloadPageLink = tag.next_sibling.get('href')
    print("Gathered the latest download version at the link: ", downloadPageLink)
    response = session.get(downloadPageLink)
    response.html.render(timeout=0, sleep=2)

    while len(response.html.links) == 0 and retryCount <= 3:
        print("Could not find link.. Retrying")
        response = session.get(downloadPageLink)
        response.html.render(timeout=0, sleep=2)
        retryCount += 1

    if len(response.html.links) != 0:
        urlList = response.html.links
        downloadLink = getUrlForOS(urlList, sys.platform)
        response = requests.get(downloadLink)
        if sys.platform == 'darwin':
            driverPath = '/usr/local/bin/chromedriver'
            os.remove(driverPath)
            downloadPath = driverPath+'.zip'
            download(response, 10, downloadPath, 'ChromeDriver - Mac')
            with zipfile.ZipFile(downloadPath, 'r') as zip_ref:
                zip_ref.extractall(os.path.dirname(downloadPath))
                os.remove(downloadPath)
            os.chmod(driverPath, stat.S_IXUSR)
        elif sys.platform == 'win32':
            driverPath = os.path.join('c','webdrivers', 'chromedriver')
            downloadPath = driverPath + '.zip'
            download(response, 10, downloadPath, 'ChromeDriver - Windows')
            with zipfile.ZipFile(downloadPath, 'r') as zip_ref:
                zip_ref.extractall(os.path.dirname(downloadPath))
                os.remove(downloadPath)
        else:
            driverPath = '/usr/bin/chromedriver'
            downloadPath = driverPath+'.zip'
            download(response, 10, downloadPath, 'ChromeDriver - Linux')
            with zipfile.ZipFile(downloadPath, 'r') as zip_ref:
                zip_ref.extractall(os.path.dirname(downloadPath))
                os.remove(downloadPath)
            os.chmod(driverPath, stat.S_IXUSR)

    else:
        print("Failed to update.  Contact Christian for help.")
        return 0
