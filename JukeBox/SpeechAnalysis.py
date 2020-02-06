import musicPlayer

import speech_recognition as sr
import random
import time
from speechPrompts import computer
import os

def recognize_speech_from_mic(recognizer,
                              microphone,
                              OS=None,
                              string_to_say=None,
                              talking=False,
                              file_to_play=None,
                              active=False):
    """Transcribe speech from recorded from `microphone`.
    Returns a dictionary with three keys:
    "success": a boolean indicating whether or not the API request was
               successful
    "error":   `None` if no error occured, otherwise a string containing
               an error message if the API could not be reached or
               speech was unrecognizable
    "transcription": `None` if speech could not be transcribed,
               otherwise a string containing the transcribed text
    """
    # check that recognizer and microphone arguments are appropriate type
    if not isinstance(recognizer, sr.Recognizer):
        raise TypeError("`recognizer` must be `Recognizer` instance")

    if not isinstance(microphone, sr.Microphone):
        raise TypeError("`microphone` must be `Microphone` instance")

    # adjust the recognizer sensitivity to ambient noise and record audio
    # from the microphone
    with microphone as source:
        # if active == False:
        print('Hold on, I am adjusting to the ambience of the room')
        recognizer.adjust_for_ambient_noise(source)
        if talking == True:
            computer.speak(OS, string_to_say, file_to_play=file_to_play)
            print("Speak Now.")
        if talking == False:
            print("Speak Now.")
        audio = recognizer.listen(source)

    # set up the response object
    response = {
        "success": True,
        "error": None,
        "transcription": None
    }

    # try recognizing the speech in the recording
    # if a RequestError or UnknownValueError exception is caught,
    #     update the response object accordingly
    try:
        # uncomment to use pocketsphinx
        # response["transcription"] = recognizer.recognize_google(audio)

        if active == False:
            response["transcription"] = recognizer.recognize_google(audio)

        if active == True:
            response["transcription"] = recognizer.recognize_google(audio)

    except sr.RequestError:
        # API was unreachable or unresponsive
        response["success"] = False
        response["error"] = "API unavailable"
    except sr.UnknownValueError:
        # speech was unintelligible
        response["error"] = "Unable to recognize speech"

    return response


def main(mic,
         r,
         OS='',
         string_to_say='',
         talking=False,
         file_to_play=None,
         searchList=[],
         pathToDirectory=''):

    response = recognize_speech_from_mic(r,
                                         mic,
                                         OS,
                                         string_to_say=string_to_say,
                                         talking=talking,
                                         file_to_play=file_to_play)

    while response['success'] == False or response['error'] != None:
        print('Error. Try again')
        response = recognize_speech_from_mic(r,
                                             mic,
                                             OS,
                                             string_to_say='Error try again',
                                             talking=talking,
                                             file_to_play=os.path.join(pathToDirectory,'speechPrompts', 'tryAgain.m4a'))

    if response['success'] == True:
        print('You said: ', response['transcription'])
        searchList = response["transcription"].lower().replace("'",'').split(' + ')
    return searchList

if __name__=="__main__":
    mic = sr.Microphone()
    r = sr.Recognizer()
    text = main(mic, r)
