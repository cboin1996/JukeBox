import vlc
import os, sys
import time
import speechanalysis
from speechprompts import computer
from features import tools
import globalvariables
import glob
from itunes import itunes, search
import random

if sys.platform != 'win32':
    import termios, tty, select, atexit
    from select import select
else:
    import msvcrt

def play_file(prompt, file_path, startup_time=1.5, song_index=0, index_diff=0, microphone=None, recognizer=None, speech_recog_enabled=False, command_string=''):
    vlc_instance = vlc.Instance()
    player = vlc_instance.media_player_new()
    media = vlc_instance.media_new(file_path)
    media.get_mrl()
    player.set_media(media)
    player.play()
    finished_playing = wait_until_end(player, prompt, song_index, index_diff, microphone=microphone, recognizer=recognizer, speech_recog_enabled=speech_recog_enabled, command_string=command_string)
    return finished_playing
# VLC STATES 
# {0: 'NothingSpecial',
#  1: 'Opening',
#  2: 'Buffering',
#  3: 'Playing',
#  4: 'Paused',
#  5: 'Stopped',
#  6: 'Ended',
#  7: 'Error'}

def wait_until_end(player, prompt, file_index, index_diff, microphone, recognizer, speech_recog_enabled=False, command_string=globalvariables.PLAYING_STRING_COMMANDS_DEFAULT):
    paused = False
    Ended = 6 # code for ended in vlc
    Paused = 4
    Playing = 3
    Stopped = 5
    kb = tools.KBHit()
    command = ' '
    print(prompt)
    current_state = player.get_state()
    while current_state != Ended and current_state != Stopped: # return the action if there is one
        setting = None
        if speech_recog_enabled == True:
            command, setting = speech_listen_for_keyword(microphone, recognizer, key_word='hello jukebox', player=player, phrase_time_limit=4.5)
            if command == 'Aborted':
                speech_recog_enabled = False
                print(command_string) # output commands to user

        current_state = player.get_state() # get the state before checking user input
        time.sleep(0.5) # so the cpu isnt destroyed

        action = check_for_user_input(player, state=current_state, file_index=file_index, index_diff=index_diff,
                                      kb=kb, command=command, speech_recog_enabled=speech_recog_enabled, microphone=microphone, recognizer=recognizer, volume=setting)
        if action != None and command == 'Aborted': # once user has put action in, renable the speech recog.
            speech_recog_enabled = True
        current_state = player.get_state() # get the state before beginning next iteration

    kb.set_normal_term() # this must be outside the loop

    if current_state == Ended:
        return 'next' # go next if file ends
    else:
        return action # do the necessary action

def speech_listen_for_keyword(microphone, recognizer, key_word, base_path=sys.path[0], player=None, timeout=None, phrase_time_limit=None):

    speech_response_dict = speechanalysis.recognize_speech_from_mic(recognizer,
                                                               microphone,
                                                               talking=False,
                                                               phrase_time_limit=phrase_time_limit)
    if speech_response_dict['success'] == True and speech_response_dict['error'] == None:

        print('You said: ', speech_response_dict['transcription'])
        response = speech_response_dict["transcription"].lower().replace("'",'').split(' + ')

        if computer.interpret_command(response, True, key_word=key_word) == key_word:
            player.set_pause(1) # pause song for speech
            speech_response_dict = speechanalysis.main(microphone, recognizer,
                                                  talking=True, operating_system=sys.platform,
                                                  string_to_say="I am listening",
                                                  file_to_play=os.path.join(base_path, 'speechPrompts', 'listening.m4a'),
                                                  base_path=base_path,
                                                  phrase_time_limit=phrase_time_limit,
                                                  expected = ['resume', 'next', 'pause', 'restart', 'previous', 'stop', 'volume'])
            return computer.interpret_action(speech_response_dict)
    if speech_response_dict['error'] == 'KeyboardInterrupt':
        return 'Aborted', None
    return None, None

# index_diff is 1 upon end of the playlist.
def check_for_user_input(player, operating_system=sys.platform, state=3, file_index=0,
                        index_diff=0, kb=None, command='', speech_recog_enabled=False,
                        microphone=None, recognizer=None, base_path=sys.path[0], volume=None): # default state to playing
    # char = getch(OS)
    char = ''
    if kb.kbhit():
        char = kb.getch()

    if state == 3 and (char == ' ' or command == 'pause'):
        print('Pausing.')
        state = 4
        player.set_pause(1)
        return 'pause'
    elif char == ' ' or command == 'resume':
        print("Unpausing")
        paused = 3
        player.set_pause(0)
        return 'unpause'
    if (char == 'd'  or command == 'next') and index_diff == 1:
        print("No more songs in playlist. Type 'q' to quit")
        if speech_recog_enabled == True:
            speech_response = speechanalysis.main(microphone, recognizer,
                                                  talking=True, operating_system=sys.platform,
                                                  string_to_say="No more songs in playlist. Do you want to quit?",
                                                  file_to_play=os.path.join(base_path, 'speechPrompts', 'noMoreDoYouQuit.m4a'),
                                                  base_path=base_path,
                                                  phrase_time_limit=4,
                                                  expected=['yes', 'no'])
            if 'yes' in computer.interpret_command(speech_response, only_command=True):
                player.stop()
                return globalvariables.player_stop
            else:
                player.set_pause(0)
                return None

    elif char == 'd' or command == 'next':
        print("Playing Next")
        player.stop()
        return 'next'

    if char == 'q' or command == globalvariables.player_stop:
        print("Quitting playlist.")
        player.stop()
        return globalvariables.player_stop

    if char == 'a' or command == 'restart':
        print("Restarting Song.")
        player.stop()
        return 'restart'

    if char == '0' or char == '1' or char == '2' or char == '3' or char == '4' or \
       char == '5' or char == '6' or char == '7' or char == '8' or char == '9':
        if char == '0':
            volume_from_user = 100
            
        else:
            volume_from_user = int(char) * 10
    
        print("Setting volume to %s" % (volume_from_user))
        player.audio_set_volume(volume_from_user)

    if (char == 'z' or command == 'previous') and file_index==0 :
        print("Can't go backwards. This is the first song.")
        if speech_recog_enabled == True:
            speech_response = speechanalysis.main(microphone, recognizer,
                                                  operating_system=sys.platform,
                                                  talking=True,
                                                  string_to_say="Cannot go backwards. Do you want to restart the song?",
                                                  file_to_play=os.path.join(base_path, 'speechPrompts', 'cantBackDoRestart.m4a'),
                                                  base_path=base_path,
                                                  phrase_time_limit=4,
                                                  expected=['yes', 'no'])
            if 'yes' in computer.interpret_command(speech_response, only_command=True):
                player.stop()
                return 'restart'
            else:
                player.set_pause(0)
                return None

    elif char == 'z' or command == 'previous':
        print("Moving back a song.")
        player.stop()
        return 'rewind'

    if command == 'volume' and volume != None:
        print('Set volume to %s' %(volume))
        player.audio_set_volume(volume)
        player.set_pause(0)
        return None
    elif command == 'volume' and volume == None:
        print("No volume percent given.")
        player.set_pause(0)
        return None

    return None # user made no choice

def play_in_order(song_paths, speech_recog_enabled, path_to_directory, speech_string='', speech_path='', mic=None, r=None):
    """
    Begins playing through a list of songs in order
    params: iTunes song paths dict, speech recognition command, path to root script folder,
        output speech text, audiofile path for speech prompt (windows), microphone object,
        speech recognizer object
    Returns: None
    """
    wait_until_end = ''
    if speech_recog_enabled == True:
        computer.speak(sys.platform,
                       speech_string,
                       os.path.join(path_to_directory, 'speechPrompts', speech_path)
                       )
    print(globalvariables.PLAYING_STRING_COMMANDS_DEFAULT) # provide commands
    i = 0
    while i < len(song_paths):
        song = song_paths[i].split(os.sep)
        if speech_recog_enabled == True:
            computer.speak(sys.platform,
                           "Playing: %s." % (tools.strip_file_for_speech(song[len(song)-1])),
                           os.path.join(path_to_directory, 'speechPrompts', 'playingSong.m4a')
                           )
        wait_until_end = play_file(globalvariables.PLAYING_STRING_DEFAULT % (song[len(song)-3], #3 is album
                                                                                     song[len(song)-2], #2 is artist
                                                                                     song[len(song)-1]), #1 is song
                                                                                     song_paths[i],
                                                                                     song_index=i,
                                                                                     index_diff=len(song_paths)-i,
                                                                                     microphone=mic, recognizer=r, speech_recog_enabled=speech_recog_enabled,
                                                                                     command_string=globalvariables.PLAYING_STRING_COMMANDS_SPECIAL)
        if wait_until_end == 'rewind' and i != 0: # break loop if user desires it to be.
            i = i-1 # play previous

        if wait_until_end == 'next':
            i = i+1 # play next song
        if wait_until_end == globalvariables.player_stop: # break loop if user desires it to be.
            break # quit

def play_found_songs(song_paths,
                    auto_download_enabled,
                    speech_recog_on=None,
                    base_path='',
                    command='',
                    microphone=None,
                    recognizer=None,
                    is_itunes_installed=False):
    """
    Asks user if they want to play a song if there are any.
    params: iTunes song paths dict, autodownload mode enabled, speech recognition mode enabled,
        path to root script folder, speech recognition command, microphone object,
        speech recognition object
    Return: True is song is found/research/skip, else false
    """
    artists = [] # will hold list of artists
    song_names = [] # need to be zeroed out here DO NOT MOVE into parameter.
    albums = []
    song_choice = ''
    if len(song_paths) == 0:
        print("File not found on computron.. Searching iTunes API")
        return False
    else:
        # get the first item of the songs returned from the list of song paths matching
        # plays song immediatly, so return after this executes
        
        i = 0
        output_folder = "iTunes" if is_itunes_installed else "dump"
        print(f"Found these songs in your {output_folder} folder")
        for song_path in song_paths:
            song_name = song_path.split(os.sep)
            song_names.append(song_name[len(song_name)-1])

            if is_itunes_installed:
                artists.append(song_name[len(song_name)-3])
                albums.append(song_name[len(song_name)-2])
                print('  %d \t- %s - %s: %s' % (i, albums[i], artists[i], song_names[i]))
            else:
                print(f" {i} \t- {song_names[i]}")
            i += 1
        
        # autoDownload condition
        if auto_download_enabled == True:
            print("Song name too similar to one or more of above! Skipping.")
            return True

        if speech_recog_on == False:

            print('Which one(s) do you want to hear (e.g. 0 1 3)?')
            user_input_string = "OR type 'se' (perform search), 'ag' (search again/skip), 'sh' (shuffle), 'pl' (play in order), '406' (return home): "
            song_choice = tools.choose_items(input_string=user_input_string, props_lyst=song_paths)

        if speech_recog_on == True and command == 'shuffle':
            song_choice = 'sh'

        elif speech_recog_on == True and command == 'play':
            song_choice = 'pl'

        elif speech_recog_on == True and command == 'single':
            song_paths = [song_paths[0]] # select first song, data requires list
            play_in_order(song_paths, speech_recog_on, base_path, "Single Mode Activated", 'singleModeOn.m4a', mic=microphone, r=recognizer)
            return True
        if song_choice == 'ag':
            print('Returning to beginning.')
            return True
        if song_choice == globalvariables.quit_string:
            print("Exiting to home.")
            return globalvariables.quit_string

        # shuffle algorithm TODO: move to a function
        if song_choice == 'sh':
            random.shuffle(song_paths)
            play_in_order(song_paths, speech_recog_on, base_path, "Shuffle Mode Activated", 'shuffleModeOn.m4a', mic=microphone, r=recognizer)
            return True

        elif song_choice == 'se':
            return False

        elif song_choice == 'pl':
            play_in_order(song_paths, speech_recog_on, base_path, "Ordered Mode Activated", 'orderModeOn.m4a', mic=microphone, r=recognizer)
            return True

        # play the song(s) only if they want, otherwise continute with program.
        else:
            if speech_recog_on == False:
                song_paths = song_choice
                play_in_order(song_paths, speech_recog_on, base_path, mic=microphone, r=recognizer)

            return True

def find_songs(song_path_template, song_query):
    song_paths = glob.glob(song_path_template)
    return [song for song in song_paths if song_query in song.lower()]