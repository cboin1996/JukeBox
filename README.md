# youtubeMP3 V 1.0.2 Official Release

![GitHub last commit](https://img.shields.io/github/last-commit/cboin1996/WebTools)


This application is a youtube scraper, audio player, iTunes integrated application. It can connect with itunes to download any album using youtube that you want, in an itunes formatted way. As of right now it's a CLI application.

### Dependencies:

Ensure upgrade pip and setuptools: 

```python
pip3 install --upgrade setuptools
pip3 install --upgrade pip
```

[ffmpeg](https://www.ffmpeg.org/)

[VLC](https://www.videolan.org/vlc/index.html) (MAKE SURE 64 BIT FOR WINDOWS)

[Python](https://www.python.org/) (Note: Please use with python 3.6.. port audio only installs properly with 3.6 as of right now)

[iTunes](https://www.apple.com/ca/itunes/)

[Chromedriver](https://chromedriver.storage.googleapis.com/index.html?path=2.45/) 

See tutorial [here](https://www.youtube.com/watch?v=dz59GsdvUF8) for installing Chromedriver on windows
For Mac --  place .exec into /usr/local/bin
Windows -- update PATH -- right click mycomputer, advanced settings, environment   	variables, etc.  Follow tutorial for detailed steps.  Restart cmd when done.


### WINDOWS INSTALLATION INSTRUCTIONS:

download **ffmpeg** for extracting audio files: [ffmpeg](https://ffmpeg.org/releases/ffmpeg-4.2.2.tar.bz2)
Navigate the directory and run setup:  

```bash
py -3 setup.py install
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






