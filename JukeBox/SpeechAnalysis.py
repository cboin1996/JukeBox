import iTunesSearch
import musicPlayer

import speech_recognition as sr
import random
import time

def recognize_speech_from_mic(recognizer, microphone):
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
        recognizer.adjust_for_ambient_noise(source, duration=3)
        print('Speak now human. I am your servant.')
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
        response["transcription"] = recognizer.recognize_sphinx(audio)
    except sr.RequestError:
        # API was unreachable or unresponsive
        response["success"] = False
        response["error"] = "API unavailable"
    except sr.UnknownValueError:
        # speech was unintelligible
        response["error"] = "Unable to recognize speech"

    return response


def main(mic, r, searchList=[]):


    print('Hold on, I am adjusting to the ambience of the room')
    response = recognize_speech_from_mic(r, mic)

    while response['success'] == False:
        print('Error. Try again')
        response = recognize_speech_from_mic(r, mic)

        if response['success'] == True:
            print('You said: ', response["transcription"])
            searchList.append(response["transcription"])

    if response['success'] == True:
        print('You said: ', response['transcription'])
        searchList.append(response["transcription"])

    return searchList

if __name__=="__main__":
    mic = sr.Microphone()
    r = sr.Recognizer()
    text = main(mic, r)