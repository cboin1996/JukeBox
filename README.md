# youtubeMP3 V 2.1 Official Release

![GitHub last commit](https://img.shields.io/github/last-commit/cboin1996/WebTools)


This application is a youtube scraper, audio player, iTunes integrated application. It can connect with itunes to download any album using youtube that you want, in an itunes formatted way. As of right now it's a CLI application.

### Dependencies:

Ensure upgrade pip and setuptools: 

```python
pip3 install --upgrade setuptools
pip3 install --upgrade pip
```


[VLC](https://www.videolan.org/vlc/index.html) (MAKE SURE 64 BIT FOR WINDOWS)

[Python](https://www.python.org/) (Note: Please use with python 3.6.. port audio only installs properly with 3.6 as of right now)

<<<<<<< HEAD
[iTunes](https://www.apple.com/ca/itunes/) (Note: you can use without iTunes. Local storage is supported as well as google drive with gdrive API)
=======
[iTunes](https://www.apple.com/ca/itunes/)

[Chromedriver](https://chromedriver.storage.googleapis.com/index.html?path=2.45/) 

See tutorial [here](https://www.youtube.com/watch?v=dz59GsdvUF8) for installing Chromedriver on windows

For Mac --  place .exec into /usr/local/bin

Windows -- update PATH -- right click mycomputer, advanced settings, environment   	variables, etc.  Follow tutorial for detailed steps.  Restart cmd when done.
>>>>>>> 6bc03efaddf695f5416e7e951491cbd029d6ce9d

This program uses chromedriver and ffmpeg.  These programs should be automatically installed on mac or windows upon the first run of the program.  Chromedriver will be automatically updated when needed by the program.

### WINDOWS INSTALLATION INSTRUCTIONS:
Navigate the directory and run setup:  

```bash
python -m venv venv
venv\Scripts\activate
python setup.py install
```

If libmagic fails, try:            
```bash
py -3 -m pip uninstall python-magic
```

If above does not work — try:      
```bash
py -3 -m pip install python-magic-bin==0.4.14
```

### MACOS INSTALLATION INSTRUCTIONS:

First Install **pyAudio**:
```bash       
brew install portaudio
pip3 install pyaudio
```

Install ffmpeg for extracting audio files: 
```bash
brew install ffmpeg
```

Configure your virtual env in the root directory WebTools
```bash
python3 -m venv venv
source\venv\activate
```

Navigate the directory and run setup:         
```bash
python3 setup.py install
```

If libmagic fails, try:            
```bash
py -3 -m pip uninstall python-magic
```

If above does not work — try:      
```bash
py -3 -m pip install python-magic-bin==0.4.14
```

### KNOWN ISSUES:

pyaudio often doesn't install on windows -- need c++ library.
Maybe try this link? : http://go.microsoft.com/fwlink/?LinkId=691126&fixForIE=.exe






