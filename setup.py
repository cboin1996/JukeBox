from setuptools import setup, find_packages
import globalvariables

setup(name='youtubetomp3',
      version=globalvariables.VERSION_NUMBER,
    install_requires=[
     'requests==2.26.0',
     'bs4==0.0.1',
     'selenium==4.0.0',
     'tqdm==4.62.3',
     'eyed3==0.9.6',
     'click==8.0.3',
     'python-magic==0.4.25',
     'speechrecognition==3.8.1',
     'pyaudio==0.2.11',
     'python-vlc==3.0.12118',
     'requests-html==0.10.0',
     'yt-dlp==2022.4.8',
     'google-api-python-client==2.30.0',
     'google-auth-httplib2==0.1.0',
     'google-auth-oauthlib==0.4.6',
     'pydub==0.25.1',
     'ffprobe-python==1.0.3',
     'mutagen==1.45.1'
     ],
     packages=find_packages()
)
