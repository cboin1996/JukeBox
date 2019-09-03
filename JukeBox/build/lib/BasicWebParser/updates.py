import requests

def chromeDriver(url):
    response = requests.get(url)
    print(response.text)
