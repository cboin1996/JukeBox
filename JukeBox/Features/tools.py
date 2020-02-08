def format_input_to_list(input_string='', list_to_compare_to=[], mode=''):
    success = False
    while True:
        user_input = input(input_string)
        if user_input == '' and mode=='remove': # no songs to remove by user, so return
            return list_to_compare_to # return unmodified list
        elif user_input == '' and mode=='choose':
            print("Come on. You gotta give me something to work with.")
            continue
        elif user_input == 'ag':
            return 'ag'
        elif user_input == '406':
            return '406'
        elif user_input == 'you':
            return 'you'
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
                elif int(char) < len(list_to_compare_to)-1 and int(char) >= 0:
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

def stripFileForSpeech(file_name):
    return file_name.replace('.mp3','').replace('&', 'and').replace('(', '').replace(')', '').replace("'", '')
