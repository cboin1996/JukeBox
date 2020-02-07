import glob

import requests
import json
import os
import eyed3
from Features import tools
# prints list from top down so its more user friendly, items are pretty big
def prettyPrinter(listOfDicts):
    i = len(listOfDicts) - 1
    print("------------------------")
    for element in reversed(listOfDicts):
        print(i, end='')
        for k,v in element.items():
            print('\t%s - %s' % (k, v))
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
    trackName='trackName'
    artistName='artistName'
    collectionName='collectionName'
    artworkUrl100='artworkUrl100'
    primaryGenreName='primaryGenreName'
    track_num='trackNumber'
    track_count='trackCount'
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
    audiofile.tag.track_num = (dictionaryOfTags[track_num], dictionaryOfTags[track_count])


    if response.status_code == 200:
        audiofile.tag.images.set(type_=3, img_data=response.content, mime_type='image/png', description=u"Art", img_url=None)

    print("Your tags have been set.")

    audiofile.tag.save()

    return dictionaryOfTags[trackName]

# entity is usually song for searching songs
def parseItunesSearchApi(searchVariable='', limit=20, entity='', autoDownload=False, requiredJsonKeys=[], searchOrLookup=True, mode=''):
    parsedResultsList = query_and_display(searchVariable, limit, entity, requiredJsonKeys, searchOrLookup)

    print('Searched for: %s' % (searchVariable))
    print('Select the number for the properties you want.. [%d to %d]'% (0, len(parsedResultsList)-1))

    # autoDownload check
    if autoDownload == False:
        if mode == 'alb':
            trackPropertySelectionNumber = int(input('Nothing here you like? 404, 406 to return home: '))
        else:
            trackPropertySelectionNumber = int(input('Nothing here? -- type 404. Save without properties -- 405, 406 -- return home: '))

    # autodownload true, set no properties.. continue on
    else:
        if len(parsedResultsList) == 0:

            trackPropertySelectionNumber = 405

        else:
            trackPropertySelectionNumber = 0

    # if nonetype, skip the call to mp3ID3Tagger() in your code
    if trackPropertySelectionNumber == 405:
        trackPropertySelectionNumber = 0
        print("No properties selected. Moving Along.")
        return
    if trackPropertySelectionNumber == 406:
        return '406'
    # call 404 option as last option before return because of recursion
    while trackPropertySelectionNumber not in range(0, len(parsedResultsList)) and trackPropertySelectionNumber != 404:
        trackPropertySelectionNumber = int(input("invalid input. Try Again: "))

    # call the function again to give any amount of tries to the user
    if trackPropertySelectionNumber == 404:
        newSearch = input('Type in a more specific title: ')
        return parseItunesSearchApi(searchVariable=newSearch, limit=limit, entity=entity, requiredJsonKeys=requiredJsonKeys, searchOrLookup=searchOrLookup, mode=mode)

    trackProperties = parsedResultsList[trackPropertySelectionNumber]

    print('Selecting item: %d' % (trackPropertySelectionNumber))
    for k,v in trackProperties.items():
        print(' - %s : %s' % (k, v))

    return trackProperties

def get_songs_in_album(searchVariable='',
                         limit=40, entity='', requiredJsonKeys={},
                         searchOrLookup=True):

    trackProperties = query_and_display(searchVariable=searchVariable,
                                        limit=40, entity='song',
                                        requiredJsonKeys=requiredJsonKeys,
                                        searchOrLookup=searchOrLookup)

    return trackProperties

def get_song_info(song_properties, key):
    song_info = []
    for element in song_properties:
        song_info.append(element[key])
    return song_info

def remove_songs_selected(song_properties_list, requiredJsonKeys):
    user_input = ''
    input_string = "Enter song id's (1 4 5 etc.) you dont want, type: enter (download all), 'ag' (search again), 406 (cancel): "
    user_input = tools.format_input_to_list(input_string=input_string, list_to_compare_to=song_properties_list)
    if user_input == None:
        return None
    elif user_input == '406':
        return user_input

    for index in user_input:
        print("Removing: %s: %s" % (index, song_properties_list[index][requiredJsonKeys[0]]))

    return [song for i, song in enumerate(song_properties_list) if i not in user_input]

def choose_songs_selected(song_list, input_string):
    user_input = ''
    user_input = tools.format_input_to_list(input_string=input_string, list_to_compare_to=song_list)
    if user_input == None:
        return None
    elif user_input == '406':
        return user_input
    elif user_input == 'you':
        return user_input
    elif user_input == 'sh':
        return user_input
    elif user_input == 'pl':
        return user_input

    for index in user_input:
        print("Song Added: %s: %s" % (index, song_list[index]))

    return [song for i, song in enumerate(song_list) if i in user_input]



def launch_album_mode(artist_album_string='', requiredJsonSongKeys={}, requiredJsonAlbumKeys={}, autoDownload=False, prog_vers=''):
    songs_in_album_props = None # will hold the songs in album properties in the new album feature
    album_props = None # will hold the album properties in the new album feature
    while songs_in_album_props == None or album_props == None: # ensure user has selected album they like.
        album_props = parseItunesSearchApi(searchVariable=artist_album_string, # get list of album properties for search
                                           entity='album', autoDownload=autoDownload, # pass in false for now. Users want to select album before letting her run
                                           requiredJsonKeys=requiredJsonAlbumKeys,
                                           searchOrLookup=True,
                                           mode=prog_vers)
        if album_props == '406': # error code for the func.
            return ('406', None, None)
        if album_props != None:
            songs_in_album_props = get_songs_in_album(searchVariable=album_props['collectionId'], # get list of songs for chosen album
                                                      limit=100, entity='song',
                                                      requiredJsonKeys=requiredJsonSongKeys,
                                                      searchOrLookup=False)
        if songs_in_album_props != None:
            songs_in_album_props = remove_songs_selected(song_properties_list=songs_in_album_props, requiredJsonKeys=requiredJsonSongKeys)
            if songs_in_album_props == '406':
                return ('406', None, None)


    searchList = get_song_info(song_properties=songs_in_album_props, # get list of just songs to search from the album # 1 is artist key
                               key=requiredJsonSongKeys[0]) # 0 is song key
    album_artist_list = get_song_info(song_properties=songs_in_album_props, # get list of just songs to search from the album # 1 is artist key
                                      key=requiredJsonSongKeys[1]) # 1 is artist key
    print("Conducting search for songs: %s" %(searchList))
    return (searchList, album_artist_list, songs_in_album_props)

def query_and_display(searchVariable, limit, entity, requiredJsonKeys, searchOrLookup):
    parsedResultsList = []
    resultDictionary = {}
    if searchOrLookup == True: # perform general search
        searchParameters = {'term':searchVariable, 'entity':entity, 'limit':limit}
        itunesResponse = requests.get('https://itunes.apple.com/search', params=searchParameters)
    else: # perform lookup query by itunes id
        searchParameters = {'id':searchVariable, 'entity':entity, 'limit':limit}
        itunesResponse = requests.get('https://itunes.apple.com/lookup', params=searchParameters)

    # itunesResponse = requests.get('https://itunes.apple.com/search?term=jack+johnson')
    print("Connected to: ", itunesResponse.url, itunesResponse.status_code)
    if itunesResponse.status_code == 200:
        itunesJSONDict = json.loads(itunesResponse.content)
        for searchResult in itunesJSONDict['results']:
            #print(searchResult)
            resultDictionary = {}
            if all(key in searchResult for key in requiredJsonKeys):
                for key in requiredJsonKeys:
                    resultDictionary[key] = searchResult[key]
                parsedResultsList.append(resultDictionary)
            else:
                print("Skipping song data as result lacked either a name, artist, album, artwork or genre in the API")

        prettyPrinter(parsedResultsList)
    return parsedResultsList


if __name__=="__main__":
    trackProperties = parseItunesSearchApi(searchVariable='Jack johnson', limit=20, entity='song')
    pathToScriptDirectory= os.path.dirname(os.path.realpath(__file__))
    pathToSong = pathToScriptDirectory + '/dump/Kansas - Dust in the Wind (Official Video).mp3'
    print(pathToSong)
    mp3ID3Tagger(mp3Path=pathToSong, dictionaryOfTags=trackProperties)
