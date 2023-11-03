from __future__ import print_function

import os.path

# from google.auth.transport.requests import Request
from google.oauth2.service_account import Credentials
# from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']
ITEM_SPREADSHEET_ID = '1Gw-UGppGalLABLU34sfxkqBviIzqNRDATtjimejNHMo'

PATH_TOKEN = 'data/google/token.json'
PATH_CREDENTIALS = 'data/google/credentials.json'

AVAILABLE_TARGETS = ['relic', 'crop', 'hoe', 'gloves', 'hund', 'item', 
                     'seed', 'shop',  'farm_size', 'player_level', 'random_chest']

# Will be needing to write a router

def load_sheet(target: str = 'item'):
    creds = None
    if os.path.exists(PATH_CREDENTIALS):
        creds = Credentials.from_service_account_file(PATH_CREDENTIALS, scopes=SCOPES)
    # if not creds or not creds.valid:
    #     if creds and creds.expired and creds.refresh_token:
    #         creds.refresh(Request())
    #     else:
    #         flow = InstalledAppFlow.from_client_secrets_file(PATH_CREDENTIALS, SCOPES)
    #         creds = flow.run_local_server(port=0)
    #     # Save the credentials for the next run
    #     with open(PATH_TOKEN, 'w') as token:
    #         token.write(creds.to_json())
    #         return None

    if target not in AVAILABLE_TARGETS:
        return None

    try:
        service = build('sheets', 'v4', credentials=creds)

        # Call the Sheets API
        sheet = service.spreadsheets()
        result = sheet.values().get(spreadsheetId=ITEM_SPREADSHEET_ID,
                                    range=f"{target}").execute()
        values = result.get('values', [])

        result_variable_names = sheet.values().get(spreadsheetId=ITEM_SPREADSHEET_ID,
                                                range=f"{target}!1:1").execute()
        values_variable_names = result_variable_names.get('values', [])

        if not values or not values_variable_names:
            print('No data found.')
            return None
        
        return values_variable_names, values

    except HttpError as err:
        print(err)
        return None