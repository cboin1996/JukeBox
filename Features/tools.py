import os, sys
import GlobalVariables
if sys.platform != 'win32':
    import termios, tty, select, atexit
    from select import select
else:
    import msvcrt

def format_input_to_list(input_string='', list_to_compare_to=[], mode=''):
    success = False
    while True:
        user_input = input(input_string)
        if user_input == '' and mode=='remove': # no songs to remove by user, so return
            return None # None signallying none to remove
        elif user_input == '' and mode=='choose':
            print("Come on. You gotta give me something to work with.")
            continue
        elif user_input == 'ag':
            return 'ag'
        elif user_input == GlobalVariables.quit_string:
            return GlobalVariables.quit_string
        elif user_input == GlobalVariables.perf_search_string:
            return GlobalVariables.perf_search_string
        elif user_input == 'sh':
            return 'sh'
        elif user_input == 'pl':
            return 'pl'

        user_input = user_input.split(' ')

        for i, char in enumerate(user_input): # validate each character

            try:
                if len(list_to_compare_to) == 1 and char.isdigit():
                    user_input[i] = int(user_input[i])
                    success = True
                elif int(char) < len(list_to_compare_to) and int(char) >= 0:
                    user_input[i] = int(user_input[i])
                    success = True

                else:
                    print("Numbers must be 0 or more and less than %s"%(len(list_to_compare_to)-1))

            except Exception as e:
                print("Must enter numbers separated by a single space %s" % (e))
                success = False
                break
        # this will not get reached unless successful trancsription
        if success == True:
            return user_input

def format_input_to_int(input_prompt, mask, low_bound, high_bound):
    while True:
        string = input(input_prompt)

        try:
            if string == GlobalVariables.quit_string:
                return 406
            if string == '405' and mask == 'save_no_prop':
                return 405
            if string == '404':
                return 404
            if 0 <= int(string) and high_bound >= int(string):
                return int(string)
            else:
                print("Number must be more than 0 and less than %s" % (high_bound))
        except KeyboardInterrupt:
            raise
        except:
            print("Come on. Invalid input.")

def choose_items(props_lyst, input_string):
    user_input = ''
    user_input = format_input_to_list(input_string=input_string, list_to_compare_to=props_lyst, mode='choose')
    if user_input == None:
        return None
    elif user_input == GlobalVariables.quit_string:
        return user_input
    elif user_input == GlobalVariables.perf_search_string:
        return user_input
    elif user_input == 'sh':
        return user_input
    elif user_input == 'pl':
        return user_input
    elif user_input == 'ag':
        return user_input

    for index in user_input:
        if "dump" not in props_lyst[index]:
            list_for_printing = props_lyst[index].split(os.sep)
            print("Song Added: %s -- %s - %s: %s" % (index, list_for_printing[len(list_for_printing)-3],
                                                    list_for_printing[len(list_for_printing)-2],
                                                    list_for_printing[len(list_for_printing)-1]))
        else:
            list_for_printing = props_lyst[index].split(os.sep)
            print(f"Song Added: {list_for_printing[len(list_for_printing) -1]}")

    return [props_lyst[i] for i in user_input]
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

def check_for_speech_keyboard_hit(player, OS=sys.platform, state=3, file_index=0, index_diff=0, kb=None, command=''): # default state to playing
    char = ''
    if kb.kbhit():
        char = kb.getch()

    if char == 's':
        print('Skipping speech attempt.')
        return 'skip'
    elif char == 'q':
        print('Quitting iteration')
        return 'quit'
    else:
        return None # user made no valid choice

def stripFileForSpeech(file_name):
    return file_name.replace('.mp3','').replace('&', 'and').replace('(', '').replace(')', '').replace("'", '').replace('[', '').replace(']', '')
