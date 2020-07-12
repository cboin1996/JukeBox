import glob

import requests
import json
import os, sys
import eyed3
from Features import tools
from iTunesManipulator import iTunes
import GlobalVariables
from Player import jukebox



# prints list from top down so its more user friendly, items are pretty big
def prettyPrinter(listOfDicts):
    i = len(listOfDicts) - 1
    print("------------------------")
    for element in reversed(listOfDicts):
        print(i, end='')
        for k,v in element.items():
            print('\t%s - %s' % (k, v))
            # print(GlobalVariables.artist_name + " - " + tag[GlobalVariables.artist_name])
            # print(GlobalVariables.collection_name + " - " + tag[GlobalVariables.collection_name])
            # print(GlobalVariables.artworkUrl100 + " - " + tag[GlobalVariables.artworkUrl100])
            # print(GlobalVariables.primary_genre_name + " - " + tag[GlobalVariables.primary_genre_name])
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
    """
    Tags an mp3 file at mp3Path given a dictionary of tags

    """
    # Create MP3File instance.
    print("Adding your tags.")
    print("Your file temperarily located at: ", mp3Path)
    # Have to call MP3File twice for it to work.

    # Get the image to show for a song .. but get high res
    # get album artwork from the list of sizes

    response = artworkSearcher(artworkUrl=dictionaryOfTags[GlobalVariables.artworkUrl100])

    # Set all the tags for the mp3
    audiofile = eyed3.load(mp3Path)
    audiofile.tag.artist = dictionaryOfTags[GlobalVariables.artist_name]
    audiofile.tag.album = dictionaryOfTags[GlobalVariables.collection_name]
    audiofile.tag.title = dictionaryOfTags[GlobalVariables.track_name]
    audiofile.tag.genre = dictionaryOfTags[GlobalVariables.primary_genre_name]
    audiofile.tag.track_num = (dictionaryOfTags[GlobalVariables.track_num], dictionaryOfTags[GlobalVariables.track_count])
    audiofile.tag.disc_num = (dictionaryOfTags[GlobalVariables.disc_num], dictionaryOfTags[GlobalVariables.disc_count])
    if GlobalVariables.collection_artist_name in dictionaryOfTags.keys(): # check if collection_artist_name exists before adding to tags
        audiofile.tag.album_artist = dictionaryOfTags[GlobalVariables.collection_artist_name]
    audiofile.tag.recording_date = dictionaryOfTags[GlobalVariables.release_date]

    if response.status_code == 200:
        audiofile.tag.images.set(type_=3, img_data=response.content, mime_type='image/png', description=u"Art", img_url=None)

    print("Your tags have been set.")

    audiofile.tag.save()

    return dictionaryOfTags[GlobalVariables.track_name]

# entity is usually song for searching songs
def parseItunesSearchApi(searchVariable='', limit=20, entity='', autoDownload=False, requiredJsonKeys=[], search=True, mode=''):
    parsedResultsList = query_api(searchVariable, limit, entity, requiredJsonKeys, 
                                  search, optional_keys=[GlobalVariables.collection_artist_name], 
                                  date_key=GlobalVariables.release_date)

    print('Searched for: %s' % (searchVariable))
    print('Select the number for the properties you want.. [%d to %d]'% (0, len(parsedResultsList)-1))

    # autoDownload check
    if autoDownload == False:
        if mode == GlobalVariables.alb_mode_string:
            input_prompt = 'Nothing here you like? 404, 406 to return home: '
            trackPropertySelectionNumber = tools.format_input_to_int(input_prompt, mask='', low_bound=0, high_bound=len(parsedResultsList)-1)

        else:
            input_prompt = 'Nothing here? -- type 404. Save without properties -- 405, 406 -- return home: '
            trackPropertySelectionNumber = tools.format_input_to_int(input_prompt, mask='save_no_prop', low_bound=0, high_bound=len(parsedResultsList)-1)

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
        return GlobalVariables.quit_string

    # call the function again to give any amount of tries to the user
    if trackPropertySelectionNumber == 404:
        newSearch = input('Type in a more specific title: ')
        return parseItunesSearchApi(searchVariable=newSearch, limit=limit, entity=entity, requiredJsonKeys=requiredJsonKeys, search=search, mode=mode)

    trackProperties = parsedResultsList[trackPropertySelectionNumber]

    print('Selecting item: %d' % (trackPropertySelectionNumber))
    for k,v in trackProperties.items():
        print(' - %s : %s' % (k, v))

    return trackProperties

def get_song_info(song_properties, key):
    song_info = []
    for element in song_properties:
        song_info.append(element[key])
    return song_info

def remove_songs_selected(song_properties_list, requiredJsonKeys):
    user_input = ''
    input_string = "Enter song id's (1 4 5 etc.) you dont want, type: enter (download all), 'ag' (search again), 406 (cancel): "
    user_input = tools.format_input_to_list(input_string=input_string, list_to_compare_to=song_properties_list, mode='remove')
    if user_input == None:
        return song_properties_list # return the full list
    elif user_input == 'ag':
        return 'ag'
    elif user_input == GlobalVariables.quit_string:
        return user_input

    for index in user_input:
        print("Removing: %s: %s" % (index, song_properties_list[index][requiredJsonKeys[0]]))

    return [song for i, song in enumerate(song_properties_list) if i not in user_input]

def launch_album_mode(artist_album_string='', requiredJsonSongKeys={}, requiredJsonAlbumKeys={}, autoDownload=False, prog_vers='', root_folder=None):
    """
    Returns:
        searchList: The list of songs to search youtube for
        album_props: the album metadata from iTunes Search API
        songs_in_album_props: the songs in an album with properties from iTunes Search API
    """
    
    songs_in_album_props = None # will hold the songs in album properties in the new album feature
    album_props = None # will hold the album properties in the new album feature
    iTunesPaths = iTunes.setItunesPaths(operatingSystem=sys.platform, searchFor=artist_album_string)

    if iTunesPaths != None:
        iTunesInstalled = True
        songs_to_play = iTunesPaths['searchedSongResult']
    else:
        iTunesInstalled = False
        song_paths_format = os.path.join(root_folder, "dump", "*.*")
        songs_to_play = jukebox.find_songs(song_paths_format, artist_album_string)
        
    song_played = jukebox.play_found_songs(songs_to_play, autoDownload=False, speechRecogOn=False,
                                            pathToDirectory=sys.path[0], iTunesInstalled=iTunesInstalled)
    if song_played == GlobalVariables.quit_string or song_played == True:
        return (GlobalVariables.quit_string, None, None)

    while songs_in_album_props == None or album_props == None or songs_in_album_props == 'ag': # ensure user has selected album they like.
        album_props = parseItunesSearchApi(searchVariable=artist_album_string, # get list of album properties for search
                                           entity='album', autoDownload=autoDownload, # pass in false for now. Users want to select album before letting her run
                                           requiredJsonKeys=requiredJsonAlbumKeys,
                                           search=True,
                                           mode=prog_vers)
        if album_props == GlobalVariables.quit_string: # error code for the func.
            return (GlobalVariables.quit_string, None, None)
        if album_props != None:
            songs_in_album_props = get_songs_in_album(searchVariable=album_props[GlobalVariables.collection_id], # get list of songs for chosen album
                                                      limit=album_props[GlobalVariables.track_count], entity='song',
                                                      requiredJsonKeys=requiredJsonSongKeys,
                                                      search=False)
        if songs_in_album_props != None:
            songs_in_album_props = remove_songs_selected(song_properties_list=songs_in_album_props, requiredJsonKeys=requiredJsonSongKeys)
            if songs_in_album_props == GlobalVariables.quit_string:
                return (GlobalVariables.quit_string, None, None)

            if songs_in_album_props == 'ag': # redo the loop if again is given
                continue


    searchList = get_song_info(song_properties=songs_in_album_props,
                               key=GlobalVariables.track_name) # track_name is the song name from iTunes search API

    print("Conducting search for songs: %s" %(searchList))
    return (searchList, album_props, songs_in_album_props)

def get_songs_in_album(searchVariable='',
                         limit=40, entity='', requiredJsonKeys={},
                         search=True):

    trackProperties = query_api(searchVariable=searchVariable,
                                        limit=limit, entity='song',
                                        requiredJsonKeys=requiredJsonKeys,
                                        search=search,
                                        optional_keys=[GlobalVariables.collection_artist_name],
                                        date_key=GlobalVariables.release_date)

    return trackProperties

def query_api(searchVariable, limit, entity, requiredJsonKeys, search, optional_keys=None, date_key=None):
    """
    params:
        searchVariable:
        limit: limit of the search in the api
        entity: either album, or song for now
        requiredJsonKeys: keys that must exist to grab
        search: whether to perform a search or a lookup
        optional_key (default None): keys to optionally grab if they exist (ex. CollectionGlobalVariables.artist_name is used for cases where multiple artists are given credit across an album)
    """
    parsedResultsList = []
    resultDictionary = {}
    if search == True: # perform general search
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
                if optional_keys is not None:
                    for optional_key in optional_keys:
                        if optional_key in searchResult.keys():
                            resultDictionary[optional_key] = searchResult[optional_key]
                if date_key is not None:
                    if date_key in searchResult.keys():
                        year = searchResult[date_key].split('-')[0] # grabs the year from date formatted "2015-05-20" for ex.
                        resultDictionary[date_key] = year
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
