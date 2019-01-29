import pyttsx3


def sayText(textString):

    engine = pyttsx3.init()
    engine.say(textString)
    engine.runAndWait()

if __name__=="__main__":
    text = input("Type something:")
    sayText(text)
