import glob

import requests
import json
import os, sys
import eyed3
from features import tools
from itunes import itunes
import globalvariables
from player import jukebox

def pretty_printer(listOfDicts, ignore_keys=None, special_dict=None, special_prompt=None):
    """
    prints list from top down so its more user friendly, items are pretty big
    params:
        listOfDicts: list of dictionaries to print
        ignore_keys: any keys not to print
        special_dict: dict containing keys with a specific prompt with three formattable options
        special_prompt: prompt to output for the special dict
    """
    i = len(listOfDicts) - 1
    print("------------------------")
    for element in reversed(listOfDicts):
        print(i, end='')
        for k,v in element.items():
            if special_dict is not None and ignore_keys is not None:
                if k in special_dict.keys():
                    print(special_prompt % (k, v, element[special_dict[k]]))
                
                elif k not in ignore_keys: # print the key and value if not in ignore_keys or special_dict
                    print('\t%s - %s' % (k, v))
                
            else: # (default case) print the key and value
                print('\t%s - %s' % (k, v))

        i -=1
        print("------------------------")

def artwork_searcher(artworkUrl):

    artwork_size_list = ['100x100', '500x500', '1000x1000', '1500x1500', '2000x2000', '2500x2500', '3000x3000']
    i = len(artwork_size_list) - 1

    response = requests.get(artworkUrl.replace('100x100', artwork_size_list[i]))
    while response.status_code != 200 and i != 0:
        print('- Size not found -- Trying size:', artwork_size_list[i])
        response = requests.get(artworkUrl.replace('100x100', artwork_size_list[i]))
        i -= 1

    if i == 0:
        print('Couldnt find album art. Your file wont have the art.')
        return None

    else:
        print('Found art at size: ', artwork_size_list[i])

    return response


def mp3ID3Tagger(mp3_path='', dictionary_of_tags={}):
    """
    Tags an mp3 file at mp3Path given a dictionary of tags

    """
    # Create MP3File instance.
    print("Adding your tags.")
    print("Your file temperarily located at: ", mp3_path)
    # Have to call MP3File twice for it to work.

    # Get the image to show for a song .. but get high res
    # get album artwork from the list of sizes

    response = artwork_searcher(artworkUrl=dictionary_of_tags[globalvariables.artworkUrl100])

    # Set all the tags for the mp3, all without if statement were checked for existence.
    audiofile = eyed3.load(mp3_path)
    audiofile.tag.artist = dictionary_of_tags[globalvariables.artist_name]
    audiofile.tag.album = dictionary_of_tags[globalvariables.collection_name]
    audiofile.tag.title = dictionary_of_tags[globalvariables.track_name]
    audiofile.tag.genre = dictionary_of_tags[globalvariables.primary_genre_name]
    audiofile.tag.track_num = (dictionary_of_tags[globalvariables.track_num], dictionary_of_tags[globalvariables.track_count])
    audiofile.tag.disc_num = (dictionary_of_tags[globalvariables.disc_num], dictionary_of_tags[globalvariables.disc_count])
    audiofile.tag.recording_date = dictionary_of_tags[globalvariables.release_date]

    if globalvariables.collection_artist_name in dictionary_of_tags.keys(): # check if collection_artist_name exists before adding to tags
        audiofile.tag.album_artist = dictionary_of_tags[globalvariables.collection_artist_name]


    if response.status_code == 200:
        audiofile.tag.images.set(type_=3, img_data=response.content, mime_type='image/png', description=u"Art", img_url=None)

    print("Your tags have been set.")

    audiofile.tag.save()

    return dictionary_of_tags[globalvariables.track_name]

# entity is usually song for searching songs
def parse_itunes_search_api(search_variable='', limit=20, entity='', auto_download_enabled=False, required_json_keys=[], search=True, mode=''):
    parsed_results_list = query_api(search_variable, limit, entity, required_json_keys, 
                                  search, optional_keys=[globalvariables.collection_artist_name], 
                                  date_key=globalvariables.release_date)

    print('Searched for: %s' % (search_variable))
    print('Select the number for the properties you want.. [%d to %d]'% (0, len(parsed_results_list)-1))

    # autoDownload check
    if auto_download_enabled == False:
        if mode == globalvariables.alb_mode_string:
            input_prompt = 'Nothing here you like? 404, 406 to return home: '
            track_property_selection_number = tools.format_input_to_int(input_prompt, mask='', low_bound=0, high_bound=len(parsed_results_list)-1)

        else:
            input_prompt = 'Nothing here? -- type 404. Save without properties -- 405, 406 -- return home: '
            track_property_selection_number = tools.format_input_to_int(input_prompt, mask='save_no_prop', low_bound=0, high_bound=len(parsed_results_list)-1)

    # autodownload true, set no properties.. continue on
    else:
        if len(parsed_results_list) == 0:

            track_property_selection_number = 405

        else:
            track_property_selection_number = 0

    # if nonetype, skip the call to mp3ID3Tagger() in your code
    if track_property_selection_number == 405:
        track_property_selection_number = 0
        print("No properties selected. Moving Along.")
        return
    if track_property_selection_number == 406:
        return globalvariables.quit_string

    # call the function again to give any amount of tries to the user
    if track_property_selection_number == 404:
        new_search = input('Type in a more specific title: ')
        return parse_itunes_search_api(search_variable=new_search, limit=limit, entity=entity, required_json_keys=required_json_keys, search=search, mode=mode)

    track_properties = parsed_results_list[track_property_selection_number]

    print('Selecting item: %d' % (track_property_selection_number))
    for k,v in track_properties.items():
        print(' - %s : %s' % (k, v))

    return track_properties

def get_song_info(song_properties, key):
    song_info = []
    for element in song_properties:
        song_info.append(element[key])
    return song_info

def remove_songs_selected(song_properties_list, required_json_keys):
    user_input = ''
    input_string = "Enter song id's (1 4 5 etc.) you dont want, type: enter (download all), 'ag' (search again), 406 (cancel): "
    user_input = tools.format_input_to_list(input_string=input_string, list_to_compare_to=song_properties_list, mode='remove')
    if user_input == None:
        return song_properties_list # return the full list
    elif user_input == 'ag':
        return 'ag'
    elif user_input == globalvariables.quit_string:
        return user_input

    for index in user_input:
        print("Removing: %s: %s" % (index, song_properties_list[index][required_json_keys[0]]))

    return [song for i, song in enumerate(song_properties_list) if i not in user_input]

def launch_album_mode(artist_album_string='', required_json_song_keys={}, required_json_album_keys={}, auto_download_enabled=False, prog_vers='', root_folder=None):
    """
    Returns:
        searchList: The list of songs to search youtube for
        album_props: the album metadata from iTunes Search API
        songs_in_album_props: the songs in an album with properties from iTunes Search API
    """
    
    songs_in_album_props = None # will hold the songs in album properties in the new album feature
    album_props = None # will hold the album properties in the new album feature
    itunes_paths_dict = itunes.setItunesPaths(operatingSystem=sys.platform, searchFor=artist_album_string)

    if itunes_paths_dict != None:
        is_itunes_installed = True
        songs_to_play = itunes_paths_dict['searchedSongResult']
    else:
        is_itunes_installed = False
        song_paths_format = os.path.join(root_folder, "dump", "*.*")
        songs_to_play = jukebox.find_songs(song_paths_format, artist_album_string)
        
    song_played = jukebox.play_found_songs(songs_to_play, auto_download_enabled=False, speech_recog_on=False,
                                            base_path=sys.path[0], is_itunes_installed=is_itunes_installed)
    if song_played == globalvariables.quit_string or song_played == True:
        return (globalvariables.quit_string, None, None)

    while songs_in_album_props == None or album_props == None or songs_in_album_props == 'ag': # ensure user has selected album they like.
        album_props = parse_itunes_search_api(search_variable=artist_album_string, # get list of album properties for search
                                           entity='album', auto_download_enabled=auto_download_enabled, # pass in false for now. Users want to select album before letting her run
                                           required_json_keys=required_json_album_keys,
                                           search=True,
                                           mode=prog_vers)
        if album_props == globalvariables.quit_string: # error code for the func.
            return (globalvariables.quit_string, None, None)
        if album_props != None:
            songs_in_album_props = get_songs_in_album(search_variable=album_props[globalvariables.collection_id], # get list of songs for chosen album
                                                      limit=album_props[globalvariables.track_count], entity='song',
                                                      required_json_keys=required_json_song_keys,
                                                      search=False)
        if songs_in_album_props != None:
            songs_in_album_props = remove_songs_selected(song_properties_list=songs_in_album_props, required_json_keys=required_json_song_keys)
            if songs_in_album_props == globalvariables.quit_string:
                return (globalvariables.quit_string, None, None)

            if songs_in_album_props == 'ag': # redo the loop if again is given
                continue


    search_list = get_song_info(song_properties=songs_in_album_props,
                               key=globalvariables.track_name) # track_name is the song name from iTunes search API

    print("Conducting search for songs: %s" %(search_list))
    return (search_list, album_props, songs_in_album_props)

def get_songs_in_album(search_variable='',
                         limit=40, entity='', required_json_keys={},
                         search=True):

    track_properties = query_api(search_variable=search_variable,
                                        limit=limit, entity='song',
                                        required_json_keys=required_json_keys,
                                        search=search,
                                        optional_keys=[globalvariables.collection_artist_name],
                                        date_key=globalvariables.release_date)

    return track_properties

def query_api(search_variable, limit, entity, required_json_keys, search, optional_keys=None, date_key=None):
    """
    params:
        searchVariable:
        limit: limit of the search in the api
        entity: either album, or song for now
        requiredJsonKeys: keys that must exist to grab
        search: whether to perform a search or a lookup
        optional_key (default None): keys to optionally grab if they exist (ex. CollectionGlobalVariables.artist_name is used for cases where multiple artists are given credit across an album)
    """
    parsed_results_list = []
    result_dict = {}
    if search == True: # perform general search
        search_parameters = {'term':search_variable, 'entity':entity, 'limit':limit}
        itunes_response = requests.get('https://itunes.apple.com/search', params=search_parameters)
    else: # perform lookup query by itunes id
        search_parameters = {'id':search_variable, 'entity':entity, 'limit':limit}
        itunes_response = requests.get('https://itunes.apple.com/lookup', params=search_parameters)

    # itunesResponse = requests.get('https://itunes.apple.com/search?term=jack+johnson')
    print("Connected to: ", itunes_response.url, itunes_response.status_code)
    if itunes_response.status_code == 200:
        itunes_json_dict = json.loads(itunes_response.content)
        for search_results in itunes_json_dict['results']:
            result_dict = {}
            if all(key in search_results for key in required_json_keys):
                for key in required_json_keys:
                    if key == date_key:
                        year = search_results[key].split('-')[0] # will grab the year from date formatted 2016-06-01
                        result_dict[key] = year
                    else:
                        result_dict[key] = search_results[key]

                if optional_keys is not None:
                    for optional_key in optional_keys:
                        if optional_key in search_results.keys():
                            result_dict[optional_key] = search_results[optional_key]
                parsed_results_list.append(result_dict)
            else:
                print("Skipping song data as result lacked either a name, artist, album, artwork or genre in the API")

        pretty_printer(parsed_results_list, ignore_keys=globalvariables.dont_print_keys,
                                        special_dict=globalvariables.special_print_dict,
                                        special_prompt=globalvariables.special_prompt)
    return parsed_results_list


if __name__=="__main__":
    trackProperties = parse_itunes_search_api(search_variable='Jack johnson', limit=20, entity='song')
    pathToScriptDirectory= os.path.dirname(os.path.realpath(__file__))
    pathToSong = pathToScriptDirectory + '/dump/Kansas - Dust in the Wind (Official Video).mp3'
    print(pathToSong)
    mp3ID3Tagger(mp3_path=pathToSong, dictionary_of_tags=trackProperties)
