import vlc
import os
import time
import GlobalVariables

"""
Outputs audio prompt to user based on the computer OS
args: computer operating system, speech prompt, audio file speech prompt
Returns: None
"""
def speak(OS, string_to_say, file_to_play=None):
    if OS == 'darwin':
        os.system('say ' + string_to_say)
    elif file_to_play != None:
        p = vlc.MediaPlayer(file_to_play)
        time.sleep(0.5) #startup time
        p.play()
        time.sleep(2) # play file
    return
# used in main program
"""
Interprets speech command from the list of given speech commands
args: speech text from text to speech, boolean option to alter return, key word to check for
Returns: Tuple with command and transcribed speech from text
"""
def interpret_command(speech_text, only_command=False, key_word=' '):
    list_of_commands = GlobalVariables.list_of_speech_commands

    if key_word != ' ':
        if key_word == speech_text[0].lower() and only_command==True: #shortcut -- skip the hello
            return key_word

    for command in list_of_commands:
        if command == speech_text[0].split(' ')[0] and only_command == False:
            speech_text[0] = speech_text[0].replace('%s ' %(command),'')
            return command, speech_text
        if command == speech_text[0].split(' ')[0] and only_command == True:
            return command


    return (None, None)


# used in music playback
"""
Interprets speech prompt into an action to pose on the audio player
args: transcribed text from speech
Returns: a tuple with an action and the commmand
"""
def interpret_action(speech_text):


    for action in GlobalVariables.player_actions:
        if action == 'volume':
            if '%' in speech_text[0]: # if no percent given return no volume
                volume = int(speech_text[0].split(' ')[1].replace('%', ''))
            else:
                volume = None

            return action,volume
        elif action == speech_text[0].split(' ')[0]: #shortcut -- skip the hello
            return speech_text[0].split(' ')[0], None
    if speech_text[0] not in GlobalVariables.player_actions:
        return speech_text[0].split(' ')[0], None
