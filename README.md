# youtubeMP3 V 2.3.2 Official Release

![GitHub last commit](https://img.shields.io/github/last-commit/cboin1996/WebTools)


This application is a youtube scraper, audio player, iTunes integrated application. It can connect with itunes to download any album using youtube that you want, in an itunes formatted way. As of right now it's a CLI application.

***Disclaimer:
Keep in mind this app is preliminary, and is the first project I ever made. I continue to update it as needed, but it is in need of a large refactor and proper programming around the cli interface for catching errors/parsing inputs.***

## Dependencies:
[VLC](https://www.videolan.org/vlc/index.html) (MAKE SURE 64 BIT FOR WINDOWS)

[Python](https://www.python.org/) (Note: Please use with python 3.8.

[iTunes](https://www.apple.com/ca/itunes/) (Note: you can use without iTunes. Local storage is supported as well as google drive with gdrive API)

This program uses chromedriver and ffmpeg.  These programs should be automatically installed on mac or windows upon the first run of the program.  Chromedriver will be automatically updated when needed by the program. FFMMPEG is no longer auto installed. Maybe one day Ill re-add it.

## Install on Windows:
You will need ffmpeg from [here](https://www.ffmpeg.org/download.html#build-windows).
Make sure you add the binary to your path.

### Install PyAudio Dependencies
- c++ tools: https://visualstudio.microsoft.com/visual-cpp-build-tools/
  - Launch `Visual Studio Installer` from start menu.
  - Install options, and click 'modify' and install `Desktop Development with C++`
- Install paudio wheel if the below steps dont work from here: 
  - pip install pipwin
  - pipwin install pyaudio

### If Using venv
```bash
task install:venv
venv\Scripts\activate
task venv:deps
```

### If Installing Globally
```bash
task install
```

Run the app as administrator for the first time you run the program! Otherwise your path will not be updated (some binariers like chromedriver are added to path automatically).
```bash
python3 musicPlayer.py
```
## Install on MacOS/Linux:

- First Install **pyAudio**:

[MAC]
```bash       
brew install portaudio
brew install ffmpeg
```
[LINUX]
```bash
sudo apt install portaudio19-dev
sudo apt install python3-pyaudio
sudo apt install ffmpeg
```

### If Using venv
If you like activate a venv:
```bash
task install:venv
source venv/bin/activate
task venv:deps
```

### If Installing Globally
Run the taskfile:
```bash
task install
```

## Running
```bash
python3 musicPlayer.py
```
### KNOWN ISSUES:
- ffmmpeg is no longer auto installed. youre on your own there.
