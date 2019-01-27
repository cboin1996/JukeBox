#### README:

youtubeMP3 V 1.0 Official Release


Once you have placed the package in your desired folder:

WINDOWS:


cd to the folder and type:         py -3 setup.py install

If libmagic does not install, try: py -3 -m pip install python-libmagic
If above does not work — try:      py -3 -m pip install python-magic-bin==0.4.14
For windows vlc to function:       py -3 -m pip install python-vlc
Its possible you will need:	   py -3 -m pip install click
Its possible and likely you will need: py -3 -m pip install cffi==1.7.0




MACOS:

cd to the folder and type:         python3 setup.py install

If libmagic does not install, try: pip3 install python-libmagic
If above does not work — try:      pip3 install python-magic-bin==0.4.14
If above does not work — try:      pip3 install python-magic
Its possible you will need:	   pip3 install click
cffi gives a lot of trouble: try pip install cffi


GENERAL Downloads:

- NEED TO INSTALL ChromeDriver from: https://chromedriver.storage.googleapis.com/index.html?path=2.45/

    Tutorial for windows: https://www.youtube.com/watch?v=dz59GsdvUF8

    For Mac --  place .exec into /usr/local/bin

    Windows -- update PATH -- right click mycomputer, advanced settings, environment   	variables, etc.  Follow tutorial for detailed steps.  Restart cmd when done.

    You must install download VLC
