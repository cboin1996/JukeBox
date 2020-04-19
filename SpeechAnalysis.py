import musicPlayer

import speech_recognition as sr
import random
import time
from speechPrompts import computer
import os, sys
from Player import jukebox
from Features import tools

def recognize_speech_from_mic(recognizer,
                              microphone,
                              OS=None,
                              string_to_say=None,
                              talking=False,
                              file_to_play=None,
                              active=False,
                              timeout=None,
                              phrase_time_limit=None): # used for keyboard interuption
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
    # set up the response object
    response = {
        "success": True,
        "error": None,
        "transcription": None
    }
    # check that recognizer and microphone arguments are appropriate type
    if not isinstance(recognizer, sr.Recognizer):
        raise TypeError("`recognizer` must be `Recognizer` instance")

    if not isinstance(microphone, sr.Microphone):
        raise TypeError("`microphone` must be `Microphone` instance")

    # adjust the recognizer sensitivity to ambient noise and record audio
    # from the microphone
    with microphone as source:
        sys.stdout.write('\rHold on, I am adjusting to the ambience of the room')
        try:
            recognizer.adjust_for_ambient_noise(source)
            sys.stdout.flush()
            if talking == True:
                computer.speak(OS, string_to_say, file_to_play=file_to_play)
                sys.stdout.write("\rSpeak Now.                                         ")
            if talking == False:
                sys.stdout.write("\rSpeak Now.                                         ")
            sys.stdout.flush()

            audio = recognizer.listen(source, timeout=timeout, phrase_time_limit=phrase_time_limit)
        except KeyboardInterrupt:
            print("\nSpeech Interrupted by keyboard interrupt.")
            response['success'] = False
            response['error'] = 'KeyboardInterrupt'

            try:
                time.sleep(1)
            except KeyboardInterrupt:
                print('User did two keyboard interrupts in a row. Breaking program')
                raise
            return response

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
         pathToDirectory='',
         timeout=None,
         phrase_time_limit=None,
         expected=None
         ):
    response = recognize_speech_from_mic(r,
                                         mic,
                                         OS,
                                         string_to_say=string_to_say,
                                         talking=talking,
                                         file_to_play=file_to_play,
                                          timeout=timeout,
                                          phrase_time_limit=phrase_time_limit,
                                          )
    if expected == None:
        mask = False
    else:
        if response['transcription'] != None:
            mask = (response['transcription'].split(' ')[0] not in expected) # check first word for commamnd

    while response['success'] == False or response['error'] != None or mask:
        if expected != None:
            error_prompt = 'Error. You said: %s. Expecting commands: %s. Try again now.' % (response['transcription'],tools.stripFileForSpeech("%s"%(expected)))
            print(error_prompt)
        else:
            error_prompt = 'Error. Try Again.'

        response = recognize_speech_from_mic(r,mic,OS,string_to_say=error_prompt,talking=talking,
                                             file_to_play=os.path.join(pathToDirectory,'speechPrompts', 'tryAgain.m4a'),
                                             timeout=timeout,phrase_time_limit=phrase_time_limit,
                                             )
        if expected == None and response['error'] == None: # rengerate mask each loop
            mask = False
        else:
            if response['transcription'] != None:
                mask = (response['transcription'].split(' ')[0] not in expected) # check first word for commamnd


    if response['success'] == True:
        sys.stdout.write('\rYou said: ' + response['transcription'] + '                  ')
        sys.stdout.flush()
        searchList = response["transcription"].lower().replace("'",'').split(' + ')

    return searchList

if __name__=="__main__":
    mic = sr.Microphone()
    r = sr.Recognizer()
    text = main(mic, r)
