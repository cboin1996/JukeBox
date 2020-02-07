def format_input_to_list(input_string='', list_to_compare_to=[]):
    success = True
    while True:
        user_input = input(input_string)
        if user_input == '': # no songs to remove by user, so return
            return list_to_compare_to # return unmodified list
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
            if char.isdigit() == False:
                print("Must enter numbers separated by a space")
                success = False
                return None
            elif int(char) > len(list_to_compare_to)-1:
                print("Numbers must be 0 or more and less than %s"%(len(list_to_compare_to)-1))
                success = False
                return None
            else:
                user_input[i] = int(user_input[i])

        if success != False:
            return user_input
