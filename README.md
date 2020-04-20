#### README:

youtubeMP3 V 1.0.2 Official Release

Please use with python 3.6.. port audio only installs properly with 3.6 as of right now

Before doing ANYTHING.. upgrade pip and setuptools: pip3 install --upgrade setuptools
                                                    pip3 install --upgrade pip


Once you have placed the package in your desired folder:

WINDOWS:

download ffmpeg for extracting audio files: https://ffmpeg.org/releases/ffmpeg-4.2.2.tar.bz2
cd to the folder and type:         py -3 setup.py install

If libmagic fails, try:            py -3 -m pip uninstall python-magic
If above does not work — try:      py -3 -m pip install python-magic-bin==0.4.14

MACOS:

FIRST: MUST INSTALL pyAudio:       brew install portaudio
    				                       pip3 install pyaudio
Install ffmpeg for extracting audio files: brew install ffmpeg
cd to the folder and type:         python3 setup.py install

If libmagic fails, try:            pip3 uninstall python-magic
If above does not work — try:      pip3 install python-magic-bin==0.4.14

KNOWN ISSUES:

pyaudio often doesn't install on windows -- need c++ library.
    Maybe try this link? : http://go.microsoft.com/fwlink/?LinkId=691126&fixForIE=.exe

GENERAL Downloads (macOs downloads automatically, windows requires install manual):

- NEED TO INSTALL ChromeDriver from: https://chromedriver.storage.googleapis.com/index.html?path=2.45/

    Tutorial for windows: https://www.youtube.com/watch?v=dz59GsdvUF8

    For Mac --  place .exec into /usr/local/bin

    Windows -- update PATH -- right click mycomputer, advanced settings, environment   	variables, etc.  Follow tutorial for detailed steps.  Restart cmd when done.

    You must install download VLC (MAKE SURE 64 BIT FOR WINDOWS).. https://www.videolan.org/vlc/download-windows.html