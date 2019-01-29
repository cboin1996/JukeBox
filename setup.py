from setuptools import setup

setup(name='youtubetomp3',
      version='1.0',
      long_description=open('README.txt').read(),
    install_requires=[
     'requests',
     'bs4',
     'selenium',
     'tqdm',
     'eyed3',
     'click',
     'python-magic-bin==0.4.14',
     'SpeechRecognition',
     'pyaudio',
     ],
)
