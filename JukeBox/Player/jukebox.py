import vlc
import os, sys
import time
if sys.platform != 'win32':
    import termios, tty, select, atexit
    from select import select
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
    kb = KBHit()
    print(prompt)
    current_state = player.get_state()
    while current_state != Ended and current_state != Stopped: # return the action if there is one
        action = check_for_user_input(player, state=current_state, file_index=file_index, index_diff=index_diff, kb=kb)

        current_state = player.get_state()
        time.sleep(0.25) # so the cpu isnt destroyed

    kb.set_normal_term() # this must be outside the loop
    if current_state == Ended:
        return 'next' # go next if file ends
    else:
        return action # do the necessary action

# index_diff is 1 upon end of the playlist.
def check_for_user_input(player, OS=sys.platform, state=3, file_index=0, index_diff=0, kb=None): # default state to playing
    # char = getch(OS)
    char = ''
    if kb.kbhit():
        char = kb.getch()

    if state == 3 and char == ' ':
        print('Pausing.')
        state = 4
        player.pause()
    elif char == ' ':
        print("Unpausing")
        paused = 3
        player.pause()
    elif char == 'd' and index_diff == 1:
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

class KBHit:

    def __init__(self):
        '''Creates a KBHit object that you can call to do various keyboard things.
        '''

        if os.name == 'nt':
            pass

        else:

            # Save the terminal settings
            self.fd = sys.stdin.fileno()
            self.new_term = termios.tcgetattr(self.fd)
            self.old_term = termios.tcgetattr(self.fd)

            # New terminal setting unbuffered
            self.new_term[3] = (self.new_term[3] & ~termios.ICANON & ~termios.ECHO)
            termios.tcsetattr(self.fd, termios.TCSAFLUSH, self.new_term)

            # Support normal-terminal reset at exit
            atexit.register(self.set_normal_term)


    def set_normal_term(self):
        ''' Resets to normal terminal.  On Windows this is a no-op.
        '''

        if os.name == 'nt':
            pass

        else:
            termios.tcsetattr(self.fd, termios.TCSAFLUSH, self.old_term)


    def getch(self):
        ''' Returns a keyboard character after kbhit() has been called.
            Should not be called in the same program as getarrow().
        '''

        s = ''

        if os.name == 'nt':
            return msvcrt.getch().decode('utf-8')

        else:
            return sys.stdin.read(1)


    def getarrow(self):
        ''' Returns an arrow-key code after kbhit() has been called. Codes are
        0 : up
        1 : right
        2 : down
        3 : left
        Should not be called in the same program as getch().
        '''

        if os.name == 'nt':
            msvcrt.getch() # skip 0xE0
            c = msvcrt.getch()
            vals = [72, 77, 80, 75]

        else:
            c = sys.stdin.read(3)[2]
            vals = [65, 67, 66, 68]

        return vals.index(ord(c.decode('utf-8')))


    def kbhit(self):
        ''' Returns True if keyboard character was hit, False otherwise.
        '''
        if os.name == 'nt':
            return msvcrt.kbhit()
        else:
            dr,dw,de = select([sys.stdin], [], [], 0)
            return dr != []
