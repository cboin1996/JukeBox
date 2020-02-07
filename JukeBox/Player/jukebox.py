import vlc
import os, sys
import time
if sys.platform != 'win32':
    import termios, tty
else:
    import msvcrt

def play_file(prompt, file_path, startup_time=1.5, song_index=0, index_diff=0):
    vlc_instance = vlc.Instance()
    player = vlc_instance.media_player_new()
    media = vlc_instance.media_new(file_path)
    media.get_mrl()
    player.set_media(media)
    player.play()
    finished_playing = wait_until_end(player, prompt, song_index, index_diff)
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

def wait_until_end(player, prompt, file_index, index_diff):
    paused = False
    Ended = 6 # code for ended in vlc
    Paused = 4
    Playing = 3
    Stopped = 5

    print(prompt)
    current_state = player.get_state()
    while current_state != Ended and current_state != Stopped:
        action = check_for_user_input(player, state=current_state, file_index=file_index, index_diff=index_diff)
        time.sleep(1)
        current_state = player.get_state()

    return action

# index_diff is 0 upon end of the playlist.
def check_for_user_input(player, OS=sys.platform, state=3, file_index=0, index_diff=0): # default state to playing
    char = getch(OS)
    if state == 3 and char == ' ':
        print('Pausing.')
        state = 4
        player.pause()
    elif char == ' ':
        print("Unpausing")
        paused = 3
        player.pause()
    elif char == 'd' and index_diff == 0:
        print("No more songs in playlist. Type 'q' to quit")

    elif char == 'd':
        print("Playing Next")
        player.stop()
        return 'next'

    elif char == 'q':
        print("Quitting playlist.")
        player.stop()
        return 'quit'

    elif char == 'a':
        print("Restarting Song.")
        player.stop()
        return 'restart'
    elif char == 'z' and file_index==0:
        print("Can't go backwards. This is the first song.")
    elif char == 'z':
        print("Moving back a song.")
        player.stop()
        return 'rewind'
    else: # user made no choice
        return None

def getch(OS):
    if OS == 'win32':
        if msvcrt.kbhit():
            key = msvcrt.getch()
            try:
                key = key.decode('utf-8')
            except:
                print("Error de-coding keyboard stroke")
                key = None
            return key
    else:
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(sys.stdin.fileno())
            ch = sys.stdin.read(1)

        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return ch
