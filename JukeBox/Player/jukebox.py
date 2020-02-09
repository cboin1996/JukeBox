import vlc
import os, sys
import time
import SpeechAnalysis
from speechPrompts import computer
from Features import tools

if sys.platform != 'win32':
    import termios, tty, select, atexit
    from select import select
else:
    import msvcrt

def play_file(prompt, file_path, startup_time=1.5, song_index=0, index_diff=0, mic=None, r=None, speechRecogOn=False, command_string=''):
    vlc_instance = vlc.Instance()
    player = vlc_instance.media_player_new()
    media = vlc_instance.media_new(file_path)
    media.get_mrl()
    player.set_media(media)
    player.play()
    finished_playing = wait_until_end(player, prompt, song_index, index_diff, mic=mic, r=r, speechRecogOn=speechRecogOn, command_string=command_string)
    return finished_playing
""" VLC STATES """
# {0: 'NothingSpecial',
#  1: 'Opening',
#  2: 'Buffering',
#  3: 'Playing',
#  4: 'Paused',
#  5: 'Stopped',
#  6: 'Ended',
#  7: 'Error'}

def wait_until_end(player, prompt, file_index, index_diff, mic, r, speechRecogOn=False, command_string=''):
    paused = False
    Ended = 6 # code for ended in vlc
    Paused = 4
    Playing = 3
    Stopped = 5
    kb = tools.KBHit()
    command = ''
    print(prompt)

    current_state = player.get_state()
    while current_state != Ended and current_state != Stopped: # return the action if there is one
        if speechRecogOn == True:
            command = speech_listen_for_keyword(mic, r, key_word='hello jukebox', player=player, phrase_time_limit=4.5)
            if command == 'Aborted':
                speechRecogOn = False
                print(command_string) # output commands to user

        current_state = player.get_state() # get the state before checking user input
        time.sleep(0.5) # so the cpu isnt destroyed

        action = check_for_user_input(player, state=current_state, file_index=file_index, index_diff=index_diff,
                                      kb=kb, command=command, speechRecogOn=speechRecogOn, mic=mic, r=r)
        if action != None and command == 'Aborted': # once user has put action in, renable the speech recog.
            speechRecogOn = True
        current_state = player.get_state() # get the state before beginning next iteration

    kb.set_normal_term() # this must be outside the loop

    if current_state == Ended:
        return 'next' # go next if file ends
    else:
        return action # do the necessary action

def speech_listen_for_keyword(mic, r, key_word, pathToDirectory=sys.path[0], player=None, timeout=None, phrase_time_limit=None):

    speechResponse = SpeechAnalysis.recognize_speech_from_mic(r,
                                                               mic,
                                                               talking=False,
                                                               phrase_time_limit=phrase_time_limit)
    if speechResponse['success'] == True and speechResponse['error'] == None:

        print('You said: ', speechResponse['transcription'])
        response = speechResponse["transcription"].lower().replace("'",'').split(' + ')

        if computer.interpret_command(response, True, key_word=key_word) == key_word:
            player.set_pause(1) # pause song for speech
            speechResponse = SpeechAnalysis.main(mic, r,
                                                  talking=True, OS=sys.platform,
                                                  string_to_say="I am listening",
                                                  file_to_play=os.path.join(pathToDirectory, 'speechPrompts', 'listening.m4a'),
                                                  pathToDirectory=pathToDirectory,
                                                  phrase_time_limit=phrase_time_limit,
                                                  expected = ['resume', 'next', 'pause', 'restart', 'previous', 'stop'])
            return computer.interpret_action(speechResponse) 
    if speechResponse['error'] == 'KeyboardInterrupt':
        return 'Aborted'

# index_diff is 1 upon end of the playlist.
def check_for_user_input(player, OS=sys.platform, state=3, file_index=0, index_diff=0, kb=None, command='', speechRecogOn=False, mic=None, r=None, pathToDirectory=sys.path[0]): # default state to playing
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
        if speechRecogOn == True:
            speechResponse = SpeechAnalysis.main(mic, r,
                                                  talking=True, OS=sys.platform,
                                                  string_to_say="No more songs in playlist. Do you want to quit?",
                                                  file_to_play=os.path.join(pathToDirectory, 'speechPrompts', 'noMoreDoYouQuit.m4a'),
                                                  pathToDirectory=pathToDirectory,
                                                  phrase_time_limit=4,
                                                  expected=['yes', 'no'])
            if 'yes' in computer.interpret_command(speechResponse, only_command=True):
                player.stop()
                return 'quit'
            else:
                player.set_pause(0)
                return None

    elif char == 'd' or command == 'next':
        print("Playing Next")
        player.stop()
        return 'next'

    if char == 'q' or command == 'stop':
        print("Quitting playlist.")
        player.stop()
        return 'quit'

    if char == 'a' or command == 'restart':
        print("Restarting Song.")
        player.stop()
        return 'restart'
    if (char == 'z' or command == 'previous') and file_index==0 :
        print("Can't go backwards. This is the first song.")
        if speechRecogOn == True:
            speechResponse = SpeechAnalysis.main(mic, r,
                                                  talking=True, OS=sys.platform,
                                                  string_to_say="Cannot go backwards. Do you want to restart the song?",
                                                  file_to_play=os.path.join(pathToDirectory, 'speechPrompts', 'cantBackDoRestart.m4a'),
                                                  pathToDirectory=pathToDirectory,
                                                  phrase_time_limit=4,
                                                  expected=['yes', 'no'])
            if 'yes' in computer.interpret_command(speechResponse, only_command=True):
                player.stop()
                return 'restart'
            else:
                player.set_pause(0)
                return None

    elif char == 'z' or command == 'previous':
        print("Moving back a song.")
        player.stop()
        return 'rewind'

    return None # user made no choice
