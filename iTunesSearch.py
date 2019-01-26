import glob

import requests
import json
import os
import eyed3

# prints list from top down so its more user friendly, items are pretty big
def prettyPrinter(listOfDicts):
    i = len(listOfDicts) - 1
    print("------------------------")
    for element in reversed(listOfDicts):
        print(i, end='')
        for k,v in element.items():
            print('\t' + k + " - " + v)
            # print(artistName + " - " + tag[artistName])
            # print(collectionName + " - " + tag[collectionName])
            # print(artworkUrl100 + " - " + tag[artworkUrl100])
            # print(primaryGenreName + " - " + tag[primaryGenreName])
        i -=1
        print("------------------------")

def artworkSearcher(artworkUrl):

    artworkSizeList = ['100x100', '500x500', '1000x1000', '1500x1500', '2000x2000', '2500x2500', '3000x3000']
    i = len(artworkSizeList) - 1

    response = requests.get(artworkUrl.replace('100x100', artworkSizeList[i]))
    while response.status_code != 200 and i != 0:
        print('- Size not found -- Trying size:', artworkSizeList[i])
        response = requests.get(artworkUrl.replace('100x100', artworkSizeList[i]))
        i -= 1

    if i == 0:
        print('Couldnt find album art. Your file wont have the art.')
        return None

    else:
        print('Found art at size: ', artworkSizeList[i])

    return response


def mp3ID3Tagger(mp3Path='', dictionaryOfTags={}):

    trackName = 'trackName'
    artistName = 'artistName'
    collectionName = 'collectionName'
    artworkUrl100 = 'artworkUrl100'
    primaryGenreName = 'primaryGenreName'

    # Create MP3File instance.
    print("Adding your tags.")
    print("Your file temperarily located at: ", mp3Path)
    # Have to call MP3File twice for it to work.

    # Get the image to show for a song .. but get high res
    # get album artwork from the list of sizes

    response = artworkSearcher(artworkUrl=dictionaryOfTags[artworkUrl100])

    # Set all the tags for the mp3
    audiofile = eyed3.load(mp3Path)
    audiofile.tag.artist = dictionaryOfTags[artistName]
    audiofile.tag.album = dictionaryOfTags[collectionName]
    audiofile.tag.title = dictionaryOfTags[trackName]
    audiofile.tag.genre = dictionaryOfTags[primaryGenreName]

    if response.status_code == 200:
        audiofile.tag.images.set(type_=3, img_data=response.content, mime_type='image/png', description=u"Art", img_url=None)

    print("Your tags have been set.")

    audiofile.tag.save()

    return dictionaryOfTags[trackName]
# entity is usually song for searching songs
def parseItunesSearchApi(searchVariable='', limit=20, entity=''):
    parsedResultsList = []
    trackName = 'trackName'
    artistName = 'artistName'
    collectionName = 'collectionName'
    artworkUrl100 = 'artworkUrl100'
    primaryGenreName = 'primaryGenreName'
    resultDictionary = {}

    searchParameters = {'term':searchVariable, 'entity':entity, 'limit':limit}

    itunesResponse = requests.get('https://itunes.apple.com/search', params=searchParameters)
    # itunesResponse = requests.get('https://itunes.apple.com/search?term=jack+johnson')
    print("Connected to: ", itunesResponse.url, itunesResponse.status_code)
    if itunesResponse.status_code == 200:
        itunesJSONDict = json.loads(itunesResponse.content)
        for searchResult in itunesJSONDict['results']:
            #print(searchResult)
            resultDictionary = {}
            resultDictionary.update({trackName:searchResult[trackName]})
            resultDictionary.update({artistName:searchResult[artistName]})
            resultDictionary.update({collectionName:searchResult[collectionName]})
            resultDictionary.update({artworkUrl100:searchResult[artworkUrl100]})
            resultDictionary.update({primaryGenreName:searchResult[primaryGenreName]})
            parsedResultsList.append(resultDictionary)


        # print(element)
        prettyPrinter(parsedResultsList)

    print('Select the number for the properties you want.. [%d to %d]'% (0, len(parsedResultsList)-1))
    trackPropertySelectionNumber = int(input('Nothing here? -- type 404. Save without properties -- Type 405: '))

    # if nonetype, skip the call to mp3ID3Tagger() in your code
    if trackPropertySelectionNumber == 405:
        trackPropertySelectionNumber = 0
        print("No properties selected. Moving Along.")
        return
    # call 404 option as last option before return because of recursion
    while trackPropertySelectionNumber not in range(0, len(parsedResultsList)) and trackPropertySelectionNumber != 404:
        trackPropertySelectionNumber = int(input("invalid input. Try Again: "))

    # call the function again to give any amount of tries to the user
    if trackPropertySelectionNumber == 404:
        newSearch = input('Type in a more specific song title: ')
        return parseItunesSearchApi(searchVariable=newSearch, limit=10, entity='song')

    trackProperties = parsedResultsList[trackPropertySelectionNumber]

    print('You chose item: %d' % (trackPropertySelectionNumber))
    for k,v in trackProperties.items():
        print(k + ' : ' + v)

    return trackProperties

if __name__=="__main__":
    trackProperties = parseItunesSearchApi(searchVariable='Jack johnson', limit=20, entity='song')
    pathToScriptDirectory= os.path.dirname(os.path.realpath(__file__))
    pathToSong = pathToScriptDirectory + '/dump/Kansas - Dust in the Wind (Official Video).mp3'
    print(pathToSong)
    mp3ID3Tagger(mp3Path=pathToSong, dictionaryOfTags=trackProperties)
