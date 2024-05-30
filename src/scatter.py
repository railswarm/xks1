import os.path


from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from time import sleep


# Spreadsheet ID of Google Sheet

# Main Spreadsheet
SPREADSHEET_ID = None

# Google Sheet API non-readonly scope
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

# FS path to credentials of authorized Google Account
CREDENTIALS_PATH = "secret/token.json"

# FS path to app flow credentials
APP_FLOW_CREDENTIALS_PATH = "secret/credentials.json"

# Maximum buffer length for gatherers
MESSAGE_BUFFER_MAX_LEN = 512

# Timeout for failed network operations
SEND_TIMEOUT = 10

# Amount of attempts to resend the data
SEND_ATTEMPTS = 10


def acquire_credentials(cred_path: str, app_flow_cred_path: str, scopes: list):
    """
    Acquire and verify user credentials for future usage with Google API.
    """
    creds = None

    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists(cred_path):
        creds = Credentials.from_authorized_user_file(cred_path, scopes)
    
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                app_flow_cred_path, scopes
            )
            creds = flow.run_local_server(port=0)
        
        # Save the credentials for the next run
        with open(cred_path, "w") as token:
            token.write(creds.to_json())
    
    return creds


class Scatter:
    def __init__(self):
        # Google Auth App credentials
        self.credentials = acquire_credentials(
            CREDENTIALS_PATH,
            APP_FLOW_CREDENTIALS_PATH,
            SCOPES
        )

        # Google Sheets API service
        self.service = None

        # Google Sheet API Object
        self.sheet = None
        
        # Queue for sending data
        self.send_queue = {}

        try:
            # Try to auth with obj credentials
            self.service = build(
                "sheets",
                "v4",
                credentials=self.credentials)
            
            self.sheet = self.service.spreadsheets()
        except HttpError as error:
            print(f"Failed to establish scatter: {error}")
            # Reraise
            raise error
    
    def recv(self, sheet_range: str) -> list | None:
        """
        Request data from sheet using `sheet_range`.
        
        Note that `sheet_range` looks like "Sheet!A1:Xn"
        
        Use "Sheet" if you want to collect all of the data
        """
        result = (
            self.sheet.values()
            .get(
                spreadsheetId=SPREADSHEET_ID,
                range=sheet_range
            )
            .execute()
        )

        # Can be None if nothing was found
        values = result.get("values", [])
        
        return values
    
    def send(self) -> None:
        """
        Send the data over the network directly to
        Google Sheets and insert this data into `sheet_range`.
        
        This operation will flush the queue.
        """
        
        # Iterate over all queue
        for sheet_range, values in self.send_queue.items():
            for attempt in range(1, SEND_ATTEMPTS + 1):
                try:
                    payload = {'values': values}

                    result = self.service.spreadsheets().values().append(
                        spreadsheetId=SPREADSHEET_ID,
                        range=sheet_range,
                        valueInputOption="RAW",
                        body=payload
                    ).execute()

                    # Commit successful, do not repeat sending
                    break
                except Exception as error:
                    print(f"Failed to send data over the network: {error}, attempt {attempt}.")
                    sleep(SEND_TIMEOUT)
        
        # Flush queue    
        self.send_queue = {}
    
    def queue(self, sheet_range: str, values: list) -> None:
        """
        Queue changes to sheet.
        
        Note that `sheet_range` looks like "Sheet!A1:Xn".
        """
        try:
            self.send_queue[sheet_range].append(values)
        except KeyError:
            self.send_queue[sheet_range] = [values]