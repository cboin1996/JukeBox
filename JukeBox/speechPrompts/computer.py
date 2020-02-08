import vlc
import os
import time
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
def interpret_command(speech_text, end_cond=False, key_word=' '):
    list_of_commands = ['quit', 'play', 'shuffle', 'all', 'voice', 'debug', 'auto', 'select', 'no', 'yes']

    if key_word != ' ':
        if key_word == speech_text[0].lower() and end_cond==True: #shortcut -- skip the hello
            return key_word

    for command in list_of_commands:
        if command == speech_text[0].split(' ')[0] and end_cond == False:
            speech_text[0] = speech_text[0].replace('%s ' %(command),'')
            print(command, speech_text)
            return (command, speech_text)
        if command == speech_text[0].split(' ')[0] and end_cond == True:
            return command


    return (None, None)


# used in music playback
def interpret_action(speech_text):
    actions = ['resume', 'next', 'pause', 'restart', 'previous', 'quit']
    for action in actions:
        if action == speech_text[0].split(' ')[0]: #shortcut -- skip the hello
            return speech_text[0].split(' ')[0]
    if speech_text[0] not in actions:
        return speech_text[0].split(' ')[0]
