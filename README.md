# youtubeMP3 V 2.2 Official Release

![GitHub last commit](https://img.shields.io/github/last-commit/cboin1996/WebTools)


This application is a youtube scraper, audio player, iTunes integrated application. It can connect with itunes to download any album using youtube that you want, in an itunes formatted way. As of right now it's a CLI application.

### Dependencies:
[VLC](https://www.videolan.org/vlc/index.html) (MAKE SURE 64 BIT FOR WINDOWS)

[Python](https://www.python.org/) (Note: Please use with python 3.6.5. port audio only installs properly with 3.6.5 as of right now)

[iTunes](https://www.apple.com/ca/itunes/) (Note: you can use without iTunes. Local storage is supported as well as google drive with gdrive API)

This program uses chromedriver and ffmpeg.  These programs should be automatically installed on mac or windows upon the first run of the program.  Chromedriver will be automatically updated when needed by the program.

### WINDOWS INSTALLATION INSTRUCTIONS:
Navigate the directory and run setup:  

```bash
python -m venv venv
venv\Scripts\activate
pip install --upgrade pip
pip install --upgrade setuptools
pip install requests
pip install --upgrade google-api-python-client google-auth-httplib2 google-auth-oauthlib
python setup.py install
```

If libmagic fails, try:            
```bash
pip uninstall python-magic
```

If above does not work — try:      
```bash
pip install python-magic-bin==0.4.14
```
Run your cmd as administrator for the first time you run the program! Otherwise your path will not be updated.
```bash
python musicPlayer.py
```
### MACOS INSTALLATION INSTRUCTIONS:

First Install **pyAudio**:
```bash       
brew install portaudio
pip3 install pyaudio
```

Navigate the directory and run setup:
```bash
python3 -m venv venv
source\venv\activate
pip3 install --upgrade pip
pip3 install --upgrade setuptools
pip3 install requests
pip3 install --upgrade google-api-python-client google-auth-httplib2 google-auth-oauthlib
python3 setup.py install
```
### RUN
```bash
python musicPlayer.py
```
### KNOWN ISSUES:

pyaudio often doesn't install on windows -- need c++ library.
Maybe try this link? : http://go.microsoft.com/fwlink/?LinkId=691126&fixForIE=.exe
