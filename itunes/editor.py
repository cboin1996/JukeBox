from itunes import search
import os
import shutil
import glob
        # this functionality is alpha.. doesnt quite work.  Needs to be pasted into musicPlatyer.py above have a fine day
        # while editorOrSongDownload == '0' and continueEditing != 'no':
        #     searchFor = input("(EDITOR MODE) - Enter song(s).. separated by a ';' : ")
        #     searchList = searchFor.split('; ')
        #
        #     for searchForSong in searchList:
        #         print(" - Running program for: ", searchForSong)
        #         iTunesPaths = setItunesPaths(operatingSystem, searchFor=searchForSong)
        #
        #         if iTunesPaths != None:
        #             Editor.songPropertyEdit(iTunesPaths, searchForSong=searchForSong)
        #             print('=----------Done Cycle--------=')
        #         else:
        #             print('Im sorry this is for machines with iTunes only')
        #
        #     continueEditing = input('Want to go again? (yes/no): ')
def sync_with_gdrive(gdrive_folder_path, itunes_auto_add_folder_path):
    print("--GDRIVE SECRET COMMAND--")
    if os.path.isdir(gdrive_folder_path):
        music_files = [file for file in os.listdir(gdrive_folder_path) if ".DS" not in file]
        if len(music_files) == 0:
            return print("No Files in folder.")
        print("Files to move are: %s" % (music_files))
        for file in music_files:
            file_absolute_path = os.path.join(gdrive_folder_path, file)
            file_destination = os.path.join(itunes_auto_add_folder_path, file)
            shutil.move(file_absolute_path, file_destination)
            print("Moved to iTunes: %s" % (file))
        return
    else:
        return print("No google drive installed! Check your settings.json file for correct path to gDrive folder.")

def song_property_edit(itunes_paths, search_for_song='', auto_download_enabled=False):
    artists = [] # will hold list of artists
    song_names = [] # will hold list of songNames


    if len(itunes_paths['searchedSongResult']) == 0:
        print("File not found in iTunes Library")

    else:

        # get the first item of the songs returned from the list of song paths matching
        # plays song immediatly, so return after this executes
        print("Here are song(s) in your library matching your search: ")
        i = 0
        for song_path in itunes_paths['searchedSongResult']:
            song_name = song_path.split(os.sep)
            artists.append(song_name[len(song_name)-3])
            song_names.append(song_name[len(song_name)-1])
            print('  %d \t- %s: %s' % (i, artists[i], song_names[i]))
            i += 1

        song_selection = int(input('Please enter the song you wish to reformat: '))
        while song_selection not in range(0, len(itunes_paths['searchedSongResult'])):
            song_selection = int(input('Invalid Input. Try Again'))

        print('You chose: ', song_selection)

        track_properties = search.parse_itunes_search_api(search_variable=search_for_song,
                                                            limit=10, entity='song',
                                                            auto_download_enabled=auto_download_enabled)

        # parseItunesSearchApi() throws None return type if the user selects no properties
        if track_properties != None:
            proper_song_name = search.mp3ID3Tagger(mp3_path=itunes_paths['searchedSongResult'][song_selection],
                                                        dictionary_of_tags=track_properties)

            shutil.move(itunes_paths['searchedSongResult'][song_selection], itunes_paths['autoAdd'])



            print('Placed your file into its new spot.')
        else:
            print('Skipping tagging process (No itunes properties selected)')

