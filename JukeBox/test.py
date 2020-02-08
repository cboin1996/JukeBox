import musicPlayer

import SpeechAnalysis
import speech_recognition as sr
import random
import time
from speechPrompts import computer
import os

r = sr.Recognizer()
mic = sr.Microphone()
stop_listening = SpeechAnalysis.listen_in_backround(r, mic)
print(stop_listening)
time.sleep(10)
response = stop_listening(wait_for_stop=False)

print(response)
