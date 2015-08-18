from mail_client import GoogleMailClient
from sheet_client import GoogleSheetClient
import os
import re
import time

class GoogleVoiceSheetsClient:
    """
    Class that bridges together the sheet and mail client to handle requests.
    """
    ADD_REGEX = re.compile('([A-Za-z\s]+) add (.+)', re.IGNORECASE)
    GET_REGEX = re.compile('([A-Za-z\s]+) get', re.IGNORECASE)
    HELP_STRING = 'help'

    def __init__(self, sheet_client, mail_client, polling_interval):
        self.sheet_client = sheet_client
        self.mail_client = mail_client
        self.polling_interval = polling_interval

    def start(self):
        """
        Continuously handle incoming requests.
        """
        while True:
            start_time = time.time()
            self.mail_client.handle_unread_emails(self._handle_request)

            # Don't poll too often.
            if time.time() - start_time < self.polling_interval:
                time.sleep(self.polling_interval)

    def _handle_request(self, request):
        """
        Handle incoming texts.
        """
        m = self.ADD_REGEX.match(request)
        if m:
            return self.sheet_client.add_data(m.group(1), m.group(2))
        m = self.GET_REGEX.match(request)
        if m:
            return self.sheet_client.get_data(m.group(1))
        if self.HELP_STRING in request.lower():
            return """Commands
                      *****************************************
                      (1) [name] add [phrase] - add new entry for person with name
                      (2) [name] get - get all entries for person with name"""
        else:
            return 'Invalid request.'

def main():
    email = os.environ['FROM_EMAIL_ADDRESS']
    sheet_key = os.environ['SHEET_KEY']
    mail_credentials = os.environ['GMAIL_CREDENTIALS_PATH']
    sheet_credentials = os.environ['GOOGLE_SHEETS_CREDENTIALS_PATH']
    polling_interval = int(os.environ['POLLING_INTERVAL'])

    gmc = GoogleMailClient(email, mail_credentials)
    gsc = GoogleSheetClient(sheet_key, sheet_credentials)

    gvs_client = GoogleVoiceSheetsClient(gsc, gmc, polling_interval)
    gvs_client.start()

if __name__ == '__main__':
    main()
