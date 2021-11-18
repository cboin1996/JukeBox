from setuptools import setup, find_packages
import globalvariables

setup(name='youtubetomp3',
      version=globalvariables.VERSION_NUMBER,
    install_requires=[
     'requests',
     'bs4',
     'selenium',
     'tqdm',
     'eyed3',
     'click',
     'python-magic-bin==0.4.14',
     'speechrecognition',
     'pyaudio',
     'python-vlc',
     'requests-html',
     'youtube_dl',
     'google-api-python-client',
     'google-auth-httplib2',
     'google-auth-oauthlib',
     'pydub',
     'ffprobe-python',
     'mutagen'
     ],
     packages=find_packages()
)
