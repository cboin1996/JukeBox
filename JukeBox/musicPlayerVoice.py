import iTunesSearch
import musicPlayer
import SpeechRecognitionToText

import speech_recognition as sr


def main(searchList=[]):
    mic = sr.Microphone()
    r = sr.Recognizer()

    print('Hold on, I am adjusting to the ambience of the room')
    response = SpeechRecognitionToText.recognize_speech_from_mic(r, mic)

    while response['success'] == False:
        print('Error. Try again')
        response = SpeechRecognitionToText.recognize_speech_from_mic(r, mic)

        if response['success'] == True:
            searchList.append(response["transcription"])

    if response['success'] == True:
        searchList.append(response["transcription"])

    musicPlayer.main(r=r, mic=mic, speechInputList=searchList, speechRecog=True)

if __name__=="__main__":
    main()
