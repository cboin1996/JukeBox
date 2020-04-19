from iTunesManipulator import iTunesSearch
import os
import shutil
import glob
        # this functionality is alpha.. doesnt quite work.  Needs to be pasted into musicPlatyer.py above have a fine day
        # while editorOrSongDownload == '0' and continueEditing != 'no':
        #     searchFor = input("(EDITOR MODE) - Enter song(s).. separated by a ';' : ")
        #     searchList = searchFor.split('; ')
        #
        #     for searchForSong in searchList:
        #         print(" - Running program for: ", searchForSong)
        #         iTunesPaths = setItunesPaths(operatingSystem, searchFor=searchForSong)
        #
        #         if iTunesPaths != None:
        #             Editor.songPropertyEdit(iTunesPaths, searchForSong=searchForSong)
        #             print('=----------Done Cycle--------=')
        #         else:
        #             print('Im sorry this is for machines with iTunes only')
        #
        #     continueEditing = input('Want to go again? (yes/no): ')
def syncWithGDrive(gDriveFolderPath, iTunesAutoAddFolderPath):
    print("--GDRIVE SECRET COMMAND--")
    if os.path.isdir(gDriveFolderPath):
        music_files = [file for file in os.listdir(gDriveFolderPath) if ".DS" not in file]
        if len(music_files) == 0:
            return print("No Files in folder.")
        print("Files to move are: %s" % (music_files))
        for file in music_files:
            fileAbsPath = os.path.join(gDriveFolderPath, file)
            fileDest = os.path.join(iTunesAutoAddFolderPath, file)
            shutil.move(fileAbsPath, fileDest)
            print("Moved to iTunes: %s" % (file))
        return
    else:
        return print("No google drive installed! Check your settings.json file for correct path to gDrive folder.")

def songPropertyEdit(iTunesPaths, searchForSong='', autoDownload=False):
    artists = [] # will hold list of artists
    songNames = [] # will hold list of songNames


    if len(iTunesPaths['searchedSongResult']) == 0:
        print("File not found in iTunes Library")

    else:

        # get the first item of the songs returned from the list of song paths matching
        # plays song immediatly, so return after this executes
        print("Here are song(s) in your library matching your search: ")
        i = 0
        for songPath in iTunesPaths['searchedSongResult']:
            songName = songPath.split(os.sep)
            artists.append(songName[len(songName)-3])
            songNames.append(songName[len(songName)-1])
            print('  %d \t- %s: %s' % (i, artists[i], songNames[i]))
            i += 1

        songSelection = int(input('Please enter the song you wish to reformat: '))
        while songSelection not in range(0, len(iTunesPaths['searchedSongResult'])):
            songSelection = int(input('Invalid Input. Try Again'))

        print('You chose: ', songSelection)

        trackProperties = iTunesSearch.parseItunesSearchApi(searchVariable=searchForSong,
                                                            limit=10, entity='song',
                                                            autoDownload=autoDownload)

        # parseItunesSearchApi() throws None return type if the user selects no properties
        if trackProperties != None:
            properSongName = iTunesSearch.mp3ID3Tagger(mp3Path=iTunesPaths['searchedSongResult'][songSelection],
                                                        dictionaryOfTags=trackProperties)

            shutil.move(iTunesPaths['searchedSongResult'][songSelection], iTunesPaths['autoAdd'])



            print('Placed your file into its new spot.')
        else:
            print('Skipping tagging process (No itunes properties selected)')

    return
