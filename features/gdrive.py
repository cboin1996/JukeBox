import os, sys

from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2 import service_account
from googleapiclient import http

def get_info():
    """
    Prompts user to import information about their gDrive API if they have it.
    """
    gDrive_info = {"gDriveFolderPath": "", "folder_id" : ""}
    setup_complete = False
    while not setup_complete:

        perform_setup = input('Do you want to setup google drive api [y/n]? ')
        if perform_setup == 'y':
            print("Please follow the instructions on https://developers.google.com/drive/api/v3/quickstart/python to get the credentials.json file. Save in the Webtools directory.")
            finished = False
            while not finished:
                gdrive_path = input("Enter the path to your google drive folder you want MP3's stored in (enter nothing to skip).")
                folder_id = input("Enter your google drive folder id (if you dont have one hit enter to skip).")
                if gdrive_path == '':
                    setup_complete = True
                    finished = True
                    gDrive_info["folder_id"] = folder_id
                elif os.path.exists(gdrive_path):
                    setup_complete = True
                    finished = True
                    gDrive_info["gDriveFolderPath"] = gdrive_path
                    gDrive_info["folder_id"] = folder_id
                else:
                    print("Path does not exist.")
                    gdrive_path = input("Enter the path to your google drive folder you want MP3's stored in.")
       
        elif perform_setup == 'n':
            setup_complete = True
        else:
            perform_setup = input('Invalid input. Do you want to setup google drive api [y/n]? ')
        
    return gDrive_info

def save_song(gDrive_info, song_name, song_path):
    SCOPES = ['https://www.googleapis.com/auth/drive']
    SERVICE_ACCOUNT_FILE = os.path.join(sys.path[0],'credentials.json')
    credentials = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    service = build('drive', 'v3', credentials=credentials)

    file_metadata = {'name': song_name,
                        'parents' : [gDrive_info['folder_id']]}
    media = http.MediaFileUpload(song_path,
                            mimetype='audio/jpeg')
    file = service.files().create(body=file_metadata,
                                        media_body=media,
                                        fields='id').execute()
    file_id = file.get('id')
    print('File creation successful -- ID: %s' % file_id)
    return file_id