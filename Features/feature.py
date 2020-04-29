import json
import os, sys, time

def view_instructions(file_path):
    with open(file_path,'r') as f:
        print(f.read())
    return

def updateShuffle(pathToSettings='', shuffleOn=False):
    with open(pathToSettings, 'r') as settings_file:
        settings_data = json.load(settings_file)

    settings_data['shuffleOn'] = shuffleOn
    with open(pathToSettings, 'w') as write_to_settings:
        json.dump(settings_data, write_to_settings)

def editSettings(pathToSettings='', settingSelections=''):
    with open(pathToSettings, 'r') as settings_file:
        settings_data = json.load(settings_file)


    while settingSelections != 'quit':
        i = 0
        print("Here are your settings.")
        print("=--------Descriptions--------=:")
        print("gDriveFolderPath: a folder on your computer that google drive is connected to for storing MP3's.")
        print("folder_id: a key from google drive for your folder that stores MP3's")
        print("userWantsiTunes (do not edit): indicates whether the program will prompt the user to setup iTunes. Default is yes, after setup is no.")
        print("iTunesAutoPath: The path to your automatically add to iTunes folder. If empty will attempt to find itself.")
        print("iTunesSongsPath (do not edit): The path template used to recursively search for iTunes songs. Do not edit if it exists.")
        print("iTunesBasePath: The path to your iTunes Media folder.")
        for key, val in settings_data.items():
            print("(Genre) - ", key)
            for k, v in val.items():
                print('\t' + k + '\t- ', v)

        settingGenreChoice = input("Which setting genre do you want to edit? 'quit' to quit: ")

        if settingGenreChoice == 'quit':
            print('Quitting.')
            settingSelections = settingGenreChoice
        else:
            while settingGenreChoice not in settings_data.keys():
                settingGenreChoice = input('Not a valid setting genre Dammit! Try again: ')

            print('Editing: ', settingGenreChoice)
            for key, val in settings_data[settingGenreChoice].items():
                print('\t' + key + '\t- ', val)

            settingSelections = input('Enter your setting names: (settingOne, settingTwo, etc. ): ')
            settingChangeList = settingSelections.split(', ')


            for setting in settingChangeList:
                # check for proper setting
                while setting not in settings_data[settingGenreChoice].keys():
                    setting = input("'%s' is not in the settings.  Enter a proper setting: " % (setting))

                updateSetting = input("Enter your new value for '%s': " % (setting))

                settings_data[settingGenreChoice].update({setting:updateSetting})

                with open(pathToSettings, 'w') as write_to_settings:
                    json.dump(settings_data, write_to_settings)
                    print("Setting updated. ")

            print("Here are your updated settings.")
            for key, val in settings_data.items():
                print("(Genre) - ", key)
                for k, v in val.items():
                    print('\t' + k + '\t- ', v)

            settingSelections = input("Type 'quit' to quit, anything to go again: ")
            print("--Done Update--")

def determine_mode(arguments):
    autoDownload = False
    speechRecog = False
    debugMode = False
    if arguments[0] == 'auto':
        autoDownload = True
    elif 'voice' in arguments and 'debug' in arguments:
        speechRecog = True
        debugMode = True
    elif 'voice' in arguments:
        speechRecog = True
    elif 'auto' in arguments and 'debug' in arguments:
        autoDownload = True
        debugMode = True
    elif arguments[0] == 'debug':
        debugMode = True

    else:
        return False, False, False

    return autoDownload, speechRecog, debugMode
