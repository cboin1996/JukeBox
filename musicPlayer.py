from re import S
import json
import vlc
import shutil, os, sys
import speech_recognition as sr
import time


from itunes import (itunes, editor, search)
from features import feature, tools, gdrive
from webparse import updates
import speechanalysis
from youtube import youtube
from speechprompts import computer
from player import jukebox
import globalvariables


"""
Change log
Cboin v 2.2 -- Added sep branches for new versions
            -- Modified program to use mp3 tagged song name for file name
            -- Modified program to keep track of whether there is an album artist
Cboin v 2.1 -- Added saving to google drive option
Cboin v 2.0 -- Added album downloading, speech regonition, keybinding audio playing,
                   shuffle mode and more.
Cboin v 1.0.2.1 -- patched itunes search api not returning track names.  Also patched to use latest ytmp3 html.
Cboin v 1.0.2 -- youtubetomp3 website tag changed to target=_blank,
made download smarter by retrying if taking too long

Cboin v 1.0.1 -- released to lakes computer for tests.
Added smart search to include artists, and multi song searches.
Also added autoDownload mode to be fully functional

Cboin v 1.0 -- added search functionality and worked on excpetion handling w/ try catch / userinput
"""


def name_plates(argument, argument2, debug_mode, operating_system):
    """
    Produces nameplates and determines operating system
    params: two command line argumates, debug mode on or off, operating system
    Returns: operating system
    """
    print("================================")
    print("=-Welcome to the cBoin JukeBox-=")


    if argument == True:
        print("=------Automated Edition-------=")


    if argument == False:
        print("=--------Select Edition--------=")

    if argument2 == True:
        print("=------Voice Edition Beta------=")
        if operating_system == 'darwin':
            os.system('say "Welcome to the c boin Jukebox."')

    if debug_mode == True:
        print("=----------Debug Mode----------=")

    if operating_system == 'darwin':
        print("=---------For MAC OS X---------=")

    if operating_system == 'win32':
        print("=---------For Windows----------=")

    print(f"=-------------V{globalvariables.VERSION_NUMBER}-------------=")
    print("================================")

    return operating_system

def format_filename(path_to_file, slice_key, string_to_add):
    """
    Formats a file name signalling it is done being tagged with MP3 metadata
    params: path to the file to format, slice key to insert string tag before, string to
        add to filename
    Returns: None
    """
    # very last thing to do is to add "_complt" to the mp3.  This indicated it has gone through the entire process
    index_to_insert_before = path_to_file.find(slice_key)
    formatted_song_name = path_to_file[:index_to_insert_before] + string_to_add + path_to_file[index_to_insert_before:]
    os.rename(path_to_file, formatted_song_name)
    return formatted_song_name

def save_song_with_itunes_opts(auto_download_enabled, 
                            music_player_settings, 
                            speech_recog_enabled, 
                            microphone, 
                            recognizer, 
                            base_path, 
                            itunes_paths, 
                            song_path, 
                            formatted_song_path,
                            vlc_player):
    # autoDownload check
    if auto_download_enabled == False:
        if music_player_settings['gDrive']['folder_id'] != "":
            user_input = input("Type 's' to save to itunes, 'g' to save to gDrive, anything else to save locally to 'dump' folder. ")
        else:
            user_input = input("Type 's' to save to itunes, anything else to save locally to 'dump' folder. ")

    elif speech_recog_enabled==True and auto_download_enabled == True: # speech recog check for save
        action = ''
        print(globalvariables.PLAYING_STRING_COMMANDS_DEFAULT) # provide commands
        while action != 'next': # used this block again below. Should be its own function.. but am too right now.
            action = jukebox.wait_until_end(player=vlc_player, prompt='', file_index=0,
                                index_diff=1, microphone=microphone, recognizer=recognizer, speech_recog_enabled=speech_recog_enabled, command_string=globalvariables.PLAYING_STRING_COMMANDS_DEFAULT)
            if action == globalvariables.player_stop:
                break
            vlc_player.play()
        save_or_not = speechanalysis.main(microphone,
                                            recognizer,
                                            talking=True,
                                            operating_system=sys.platform,
                                            string_to_say="Should I save to iTunes?",
                                            file_to_play=os.path.join(base_path, 'speechprompts', 'assets', 'shouldSaveToItunes.m4a'),
                                            base_path=base_path,
                                            expected=['yes', 'no'],
                                            phrase_time_limit=4
                                            )
        if 'yes' in save_or_not:
            user_input = 's'
            computer.speak(sys.platform, 'Saving to Itunes.', os.path.join(base_path, 'speechprompts', 'assets', 'savingiTunes.m4a'))

        else:
            user_input = ''
            computer.speak(sys.platform, 'Saving Locally', os.path.join(base_path, 'speechprompts', 'assets', 'savingLocal.m4a'))

    else: # autodownload check for save
        print("Saving to iTunes.. whether you like it or not.")
        user_input = 's'

    vlc_player.stop()
    # wait till player stops before renaming song to proper formatted name
    os.rename(song_path, formatted_song_path)

    if user_input == 's':
        formatted_song_name = format_filename(path_to_file=formatted_song_path, slice_key=".mp3", string_to_add="_complt")
        shutil.move(formatted_song_name, itunes_paths['autoAdd'])
        print("Moved your file to iTunes.")

    elif user_input == 'g' and music_player_settings['gDrive']['folder_id'] != "":
        gdrive.save_song(music_player_settings['gDrive'], formatted_song_path.split(os.sep)[-1], formatted_song_path)

    else:
        print("Saved your file locally.")
        format_filename(path_to_file=formatted_song_path, slice_key=".mp3", string_to_add="_complt")


def save_song_without_itunes_opts(auto_download_enabled, music_player_settings, song_path, formatted_song_path, speech_recog_enabled, microphone, recognizer, base_path, vlc_player):
    # autoDownload check
    if auto_download_enabled == False:
        if music_player_settings['gDrive']['folder_id'] != "": # check if gDrive folder exists for saving
            user_input = input("Type 'g' to save to gDrive, anything else to stop playing and save locally.")
        else:
            input("Type anything to save locally.")

    elif speech_recog_enabled == True and auto_download_enabled == True:
        print(globalvariables.PLAYING_STRING_COMMANDS_DEFAULT) # provide commands
        action = ''
        while action != 'next': # wait until user ends song. 'next is returned from wait_until_end upon completion.'
            action = jukebox.wait_until_end(player=vlc_player, prompt='', file_index=0,
                                index_diff=1, microphone=microphone, recognizer=recognizer, speech_recog_enabled=speech_recog_enabled, command_string=globalvariables.PLAYING_STRING_COMMANDS_DEFAULT)
            if action == globalvariables.player_stop:
                break
            vlc_player.play()

        computer.speak(sys.platform, 'Saving Locally', os.path.join(base_path, 'speechprompts', 'assets', 'savingLocal.m4a'))
    else: # autodownload
        print("Saving locally. Whether you like it or not.")

    vlc_player.stop()
    os.rename(song_path, formatted_song_path)
    if user_input == 'g':
        gdrive.save_song(music_player_settings['gDrive'], formatted_song_path.split(os.sep)[-1], formatted_song_path)
        return
    format_filename(path_to_file=formatted_song_path, slice_key=".mp3", string_to_add="_complt")

# this function allows the module to be ran with or without itunes installed.
# if iTunes is not installed, the files are tagged and stored in dump folder.

def run_download(microphone,
                recognizer,
                is_itunes_installed=True,
                search_string='',
                auto_download_enabled=False,
                base_path='',
                itunes_paths={},
                speech_recog_enabled=False,
                debug_mode=False,
                track_properties={},
                music_player_settings=None):
    """
    Runs the download process for a song
    params: speech recognition microphone object, speech recognition recognizer object,
        iTunes installed or note, song to search youtube for, autodownload on or not,
        path to root directory, iTunes paths with auto add and song path, speech
        recognition on or not, debug mode on or not, track properties on or not
    Returns: None
    """
    local_dump_folder = os.path.join(base_path, "dump")
    path_to_settings = os.path.join(base_path, 'settings.json')

    response = youtube.get_youtube_info_from_database(search_query={'search_query':''}, song_name=search_string)
    youtube_download_response_object = youtube.download_song_from_youtube(youtube_page_response=response,
                                                        auto_download_enabled=auto_download_enabled,
                                                        path_to_dump_folder=local_dump_folder,
                                                        path_to_settings=path_to_settings,
                                                        debug_mode=debug_mode)

    # youtubeSongDownload returns none if there is no songPath or if user wants a more specific search
    while youtube_download_response_object['error'] == '404':
        search_string = input('Please enter your more specific song: ')
        new_youtube_response_from_search = youtube.get_youtube_info_from_database(search_query={'search_query':''}, song_name=search_string)
        youtube_download_response_object = youtube.download_song_from_youtube(youtube_page_response=new_youtube_response_from_search,
                                                auto_download_enabled=auto_download_enabled,
                                                path_to_dump_folder=local_dump_folder,
                                                path_to_settings=path_to_settings,
                                                debug_mode=debug_mode)
    if youtube_download_response_object['error'] == '405': # return out if user wants to cancel.
        return

    # No none type is good news.. continue as normal
    if youtube_download_response_object['songPath'] != None and youtube_download_response_object['error'] == None:
        if speech_recog_enabled == True:
            computer.speak(sys.platform, 'Playing song.', os.path.join(base_path, 'speechprompts', 'assets', 'playingSong.m4a'))
        vlc_player = vlc.MediaPlayer(youtube_download_response_object['songPath'])
        time.sleep(1.5) #startup time
        vlc_player.play()


        # this checks to see if the user is happy with the song, only if in select edition
        if auto_download_enabled == False and speech_recog_enabled == False:
            continue_to_save = input("Hit enter if this sounds right. To try another song -- enter (no): ")

            if continue_to_save == 'no':
                print('Returning to beginning.')
                vlc_player.stop()
                return run_download(microphone=microphone,
                                    recognizer=recognizer,
                                    is_itunes_installed=is_itunes_installed,
                                    search_string=search_string,
                                    auto_download_enabled=auto_download_enabled,
                                    base_path=base_path,
                                    itunes_paths=itunes_paths,
                                    speech_recog_enabled=speech_recog_enabled,
                                    debug_mode=debug_mode,
                                    track_properties=track_properties,
                                    music_player_settings=music_player_settings)

        # parsesearchApi() throws None return type if the user selects no properties
        if track_properties != None:
            proper_song_name = search.mp3ID3Tagger(mp3_path=youtube_download_response_object['songPath'],
                                                        dictionary_of_tags=track_properties)
            formatted_song_path = os.path.join(local_dump_folder, proper_song_name + '.mp3') # renames the song's filename to match the mp3 tag
        else:
            print('Skipping tagging process (No itunes properties selected)')
            formatted_song_path = youtube_download_response_object['songPath']

        if is_itunes_installed == True:
            save_song_with_itunes_opts(auto_download_enabled, music_player_settings, speech_recog_enabled,
                                        microphone, recognizer, base_path, itunes_paths, youtube_download_response_object['songPath'], formatted_song_path,
                                        vlc_player)
        else:
            save_song_without_itunes_opts(auto_download_enabled, music_player_settings,
                                        youtube_download_response_object['songPath'],
                                        formatted_song_path, speech_recog_enabled, microphone, recognizer,
                                        base_path, vlc_player)

    if youtube_download_response_object['error'] == 'youMP3fail':
        print("YoutubeMp3 failed too many times. quitting to last menu.")
        return
    elif youtube_download_response_object['error'] == 'had_to_update':
        print("youtube-dl was updated. Please restart the program.")
        sys.exit()

def run_for_songs(microphone=None, recognizer=None, searchlist=[], auto_download_enabled=None,
                base_path=None, speech_recog_enabled=None, debug_mode=None, command=None,
                music_player_settings=None, prog_vers='', operating_system=None, search_for=None,
                required_json_song_keys=None, album_properties=None, songs_in_album_props=None):
    """
    Runs through a song search process in iTunes then youtube depending on user interaction
    params: 
        microphone: microphone object
        recognizer: speech recognizer object,
        searchlist: list of songs to search for
        auto_download_enabled: auto download mode on or off
        base_path: path to root script directory
        speech_recog_enabled: speech recognition mode on or off
        debug_mode: debug mode on or off
        command: speech recognition command
        music_player_settings: program settings from json file
        prog_vers: program version album or song download mode
        operating_system: string for computer operating system
        search_for: song to search for
        requiredJsonSongKeys: required json song keys to tag mp3's with
        album_properties: the album metadata from iTunes Search API
        songs_in_album_props: song meta data for songs in an album from iTunes Search API
    Returns: None
    """
    for i, song_to_search_for in enumerate(searchlist):
        
        print(f" - Running program for song {i + 1} of {len(searchlist)}: {song_to_search_for}")
        itunes_paths_dict = itunes.setItunesPaths(operating_system, searchFor=song_to_search_for, album_properties=album_properties)
        # '*.*' means anyfilename, anyfiletype
        # /*/* gets through artist, then album or itunes folder structure
        if itunes_paths_dict == None:
            is_itunes_installed = False
            song_paths_format = os.path.join(os.path.join(base_path, "dump"), "*.*")
            songs_to_play = jukebox.find_songs(song_paths_format, song_to_search_for)

        else:
            is_itunes_installed = True
            songs_to_play = itunes_paths_dict["searchedSongResult"]

        song_played = jukebox.play_found_songs(songs_to_play, auto_download_enabled, speech_recog_enabled, base_path, command, microphone=microphone, recognizer=recognizer, is_itunes_installed=is_itunes_installed)

        if song_played == globalvariables.quit_string: # return to home
            return

        if prog_vers == globalvariables.alb_mode_string:
            track_properties = songs_in_album_props[i]
            song_to_search_for = track_properties[globalvariables.artist_name] + ' ' + song_to_search_for
        # secret command for syncing with gDrive files.  Special feature!
        elif search_for == '1=1':
            editor.sync_with_gdrive(gdrive_folder_path=music_player_settings["gDrive"]["gDriveFolderPath"],
                                  itunes_auto_add_folder_path=itunes_paths_dict['autoAdd'])
            break

        elif song_played == False: # if song_played is True, suggests user played song or wants to skip iteration, thus perform download
            if speech_recog_enabled == True:
                response_text = speechanalysis.main(microphone,
                                                    recognizer,
                                                    talking=True,
                                                    operating_system=sys.platform,
                                                    string_to_say="File not found. Would you like to download %s" %(tools.strip_file_for_speech(search_for)),
                                                    file_to_play=os.path.join(base_path, 'speechprompts', 'assets', 'wouldyouDL.m4a'),
                                                    base_path=base_path,
                                                    expected=['yes', 'no'])
                if 'yes' in response_text: # check if user wants to download or not
                    computer.speak(sys.platform, 'Downloading.', os.path.join(base_path, 'speechprompts', 'assets', 'downloading.m4a'))
                    auto_download_enabled=True # perform autodownload for that songs
                else:
                    return

            track_properties = search.parse_itunes_search_api(search_variable=song_to_search_for,
                                                                limit=10, entity='song',
                                                                auto_download_enabled=auto_download_enabled,
                                                                required_json_keys=required_json_song_keys,
                                                                search=True)
            if track_properties == globalvariables.quit_string: # return to home entry
                return
            elif track_properties != None: # check to ensure that properties aree selected
                song_to_search_for = "%s %s" % (track_properties['artistName'], track_properties['trackName'])

        if song_played == False: # run for either album or regualar song download
            run_download(microphone=microphone,
                         recognizer=recognizer,
                         is_itunes_installed=is_itunes_installed,
                         search_string=song_to_search_for,
                         auto_download_enabled=auto_download_enabled,
                         base_path=base_path,
                         itunes_paths=itunes_paths_dict,
                         speech_recog_enabled=speech_recog_enabled,
                         debug_mode=debug_mode,
                         track_properties=track_properties,
                         music_player_settings = music_player_settings)

        print('=----------Done Cycle--------=')

# 'auto' argv will get first video.  Manual will allow user to select video.. default behaviour
# pass argv to youtubeSongDownload
"""
Main function that runs to launch the music player program
params: command line params, speech recognizer object, microphone object, iTunes paths to auto add folder and songs dict,
      speech recognizer mode on or not, debug mode on or not
Returns: None
"""
def main(argv='', recognizer=None, microphone=None, path_to_itunes_auto_add_folder={}, speech_recog_enabled=False, debug_mode = False):
    auto_download_enabled = False
    search_list = []
    required_json_song_keys = [globalvariables.track_name,
                          globalvariables.artist_name,
                          globalvariables.collection_name,
                          globalvariables.artworkUrl100,
                          globalvariables.primary_genre_name,
                          globalvariables.track_num,
                          globalvariables.track_count,
                          globalvariables.disc_num,
                          globalvariables.disc_count,
                          globalvariables.release_date]
    required_json_album_keys = [globalvariables.artist_name, globalvariables.collection_name, globalvariables.track_count, globalvariables.collection_id]
    songs_in_album_props=[]

    prog_vers = ''
    command=''
    auto_download_enabled = False
    list_of_modes = ['auto','voice','debug', 'select', 'voice debug', 'auto debug']


    # get the obsolute file path for the machine running the script
    base_path= os.path.dirname(os.path.realpath(__file__))
    local_dump_folder_path = os.path.join(base_path, 'dump')
    path_to_settings = os.path.join(base_path, 'settings.json')

    # initialize settings
    if not os.path.exists(path_to_settings):
        with open(path_to_settings, 'w') as f:
            initialized_settings = {
                                    "gDrive" : {"gDriveFolderPath": "", "folder_id" : ""},
                                    "iTunes" : {"userWantsiTunes" : "y",
                                                "iTunesAutoPath"  : "",
                                                "iTunesSongsPath" : "",
                                                "iTunesBasePath"  : ""}
                                    }
            initialized_settings["gDrive"] = gdrive.get_info()
            json.dump(initialized_settings, f)

    with open(path_to_settings, 'r') as in_file:
        music_player_settings = json.loads(in_file.read())

    # initialize dump directory
    if not os.path.exists(local_dump_folder_path):
        os.makedirs(local_dump_folder_path)

    if updates.check_for_updates():
        return 
    # check for running version
    if len(argv) > 1:
        argv.pop(0)
        auto_download_enabled, speech_recog_enabled, debug_mode = feature.determine_mode(argv)
    # initialize for speechRecogOn
    if speech_recog_enabled == True: # TODO CHANGE BACK
        microphone = sr.Microphone()
        recognizer = sr.Recognizer()

    # determine which OS we are operating on.  Work with that OS to set
    operating_system = name_plates(auto_download_enabled, speech_recog_enabled, debug_mode, sys.platform)

    continue_getting_songs = 'yes' # initialize to yes in order to trigger idle listening
    search_for = ''

    while continue_getting_songs != 'no' :
        # initialize searchList to empty each iteration
        search_list = []
        album_properties=None # album properties list default None


        if speech_recog_enabled == False:
            search_for = input("Enter song(s) [song1; song2], 'instr' for instructions, 'set' for settings, 'alb' for albums: ")
            if search_for in list_of_modes: # will be used to determine if mode chaneg has been selected
                command = search_for

            if search_for == 'set':
                prog_vers = 'set'
                feature.editSettings(pathToSettings=path_to_settings)
            elif search_for == 'instr':
                prog_vers = 'instr'
                feature.view_instructions(os.path.join(base_path, 'Instructions.txt'))

            elif search_for == globalvariables.alb_mode_string:
                prog_vers = globalvariables.alb_mode_string
                album_user_input = input("Enter artist and album name you wish to download. Type 406 to cancel: ")
                if album_user_input == globalvariables.quit_string:
                    search_list = album_user_input # will quit out.
                else:
                    search_list, album_properties, songs_in_album_props = search.launch_album_mode(artist_album_string=album_user_input,
                                                                            required_json_song_keys=required_json_song_keys,required_json_album_keys=required_json_album_keys,
                                                                            auto_download_enabled=False, prog_vers=prog_vers, root_folder=base_path)

            else:
                search_list = search_for.split('; ')
                prog_vers = ''

        else: # Speech recognition edition
            if continue_getting_songs == "yes": # idly listen if user say's yes otherwise use searchList from end of loop
                while True:
                    raw_speech_response = speechanalysis.main(microphone, recognizer, talking=False, phrase_time_limit=4)
                    command, search_list = computer.interpret_command(raw_speech_response, only_command=False)

                    if command == 'quit':
                        return
                    if command != None: # break loop if successful transcription occurs
                        break


            else: # get the next songs from previous iteration of speech
                search_list = list(continue_getting_songs)

        if command in list_of_modes: # determine which version to be in.
            command = command.split(' ')
            auto_download_enabled, speech_recog_enabled, debug_mode = feature.determine_mode(command)
            operating_system = name_plates(auto_download_enabled, speech_recog_enabled, debug_mode, sys.platform)
            if speech_recog_enabled == True: # declare microphone and recognizer instance
                microphone = sr.Microphone()
                recognizer = sr.Recognizer()
            continue # return to top of loop.

        if search_list != globalvariables.quit_string: # if it is, skip whole song playing/searching process
            # Iterate the list of songs
            run_for_songs(microphone=microphone, recognizer=recognizer, searchlist=search_list, auto_download_enabled=auto_download_enabled,
                            base_path=base_path, speech_recog_enabled=speech_recog_enabled, debug_mode=debug_mode,command=command,
                            music_player_settings=music_player_settings, prog_vers=prog_vers, operating_system=operating_system, search_for=search_for,
                            required_json_song_keys=required_json_song_keys, album_properties=album_properties,
                            songs_in_album_props=songs_in_album_props)

        if speech_recog_enabled == False:
            continue_getting_songs = input('Want to go again (yes/no): ')

        else:
            next_songs = [] # initialize to empty before ech speech read
            next_songs = speechanalysis.main(microphone,
                                              recognizer,
                                              talking=True,
                                              operating_system=operating_system,
                                              string_to_say='Say another command or no to quit.',
                                              file_to_play=os.path.join(base_path, 'speechprompts', 'assets', 'anotherone.m4a'),
                                              base_path=base_path,
                                              phrase_time_limit=4)
            new_command, continue_getting_songs = computer.interpret_command(next_songs, only_command=False)
            command = new_command # unpacking is weird. If i used command it would not update.
            if continue_getting_songs == None: # if no command is interpreted, return to idle mode
                computer.speak(sys.platform, string_to_say='No command given. Returning to idle.',
                              file_to_play=os.path.join(sys.path[0],'speechPrompts','noCommandReturnIdle.m4a'))
                continue_getting_songs = 'yes'
            elif continue_getting_songs[0] == 'no':
                break # quit
            elif continue_getting_songs[0] == 'yes':
                print("Returning to idle.")
                continue_getting_songs = 'yes'


    # editor functionality goes here (from iTunesManipulator.editor)
    print("\n================================")
    print("=--------Have a fine day-------=")
    print("================================")
    if speech_recog_enabled == True and operating_system=='darwin':
        computer.speak(operating_system, 'Goodbye.')


if __name__=="__main__":
    main(sys.argv)
