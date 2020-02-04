import vlc
import os
import time
def speak(OS, string_to_say, file_to_play=None):
    if OS == 'darwin':
        os.system('say ' + string_to_say)
    elif file_to_play != None:
        p = vlc.MediaPlayer(file_to_play)
        time.sleep(1.5) #startup time
        p.play()
        time.sleep(2) # play file
    return
