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

def interpret_command(speech_text, end_cond):
    print(speech_text)
    if 'play' == speech_text[0].split(' ')[0] and end_cond==False: #shortcut -- skip the hello
        speech_text[0] = speech_text[0].replace('play ', '') # strip play
        return ('play', speech_text)

    elif 'shuffle' == speech_text[0].split(' ')[0] and end_cond==False: #shortcut -- skip the hello
        speech_text[0] = speech_text[0].replace('shuffle ', '') # strip play
        searchList = speech_text
        return ('shuffle', speech_text)

    elif 'all' == speech_text[0].split(' ')[0] and end_cond==False: #shortcut -- skip the hello
        speech_text[0] = speech_text[0].replace('all ', '') # strip play
        searchList = speech_text
        return ('playall', speech_text)
    elif 'no' == speech_text[0].split(' ')[0] and end_cond==True: #shortcut -- skip the hello
        return speech_text[0].split(' ')[0]

    elif 'yes' == speech_text[0].split(' ')[0] and end_cond==True: #shortcut -- skip the hello
        return speech_text[0].split(' ')[0]

    elif 'voice' == speech_text[0].lower() and end_cond==False: #shortcut -- skip the hello
        return (speech_text[0].lower(), '')

    elif 'debug' == speech_text[0].lower() and end_cond==False: #shortcut -- skip the hello
        return (speech_text[0].lower(), '')

    elif 'auto' == speech_text[0].lower() and end_cond==False: #shortcut -- skip the hello
        return (speech_text[0].lower(), '')

    elif 'select' == speech_text[0].lower() and end_cond==False: #shortcut -- skip the hello
        return (speech_text[0].lower(), '')

    else:
        return (None, None)
