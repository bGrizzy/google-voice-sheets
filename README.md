google-voice-sheets
--------
SMS interface to Google Sheets using Google Voice / Gmail. Get or add data for a row based on first-column value as a key.

### Requirements
- Python 2.7
- pip

### Running Locally
- Install requirements with ```pip install -r requirements.txt```
- Run the app with ```python app.py```

### API Keys/Credentials

#### Google Drive

A service account is used to access the Google sheet. Should be stored in a JSON file. [Setup](http://gspread.readthedocs.org/en/latest/oauth2.html)

#### Google Voice / Gmail

You must forward your Google Voice texts to a Gmail account. This app takes advantage of the Google Voice feature that allows replies to texts by responding to the corresponding email thread.

OAuth2 access/refresh tokens are used to access this Gmail account. Credentials should be stored as a JSON file. I was unable to find a better way to get the credentials JSON file, but getting the file from [this script](https://developers.google.com/gmail/api/quickstart/python) works. Make sure you request offline access with at least `gmail.modify` scope, and then you should be able to use the refresh token to constantly get new access tokens.

### Environment Variables
- `SHEET_KEY`: Key to target Google Sheet
- `POLLING_INTERVAL`: (seconds) How often to poll Gmail inbox for new requests
- `FROM_EMAIL_ADDRESS`: Email address you receive / send Google Voice emails from
- `GMAIL_CREDENTIALS_PATH`: Path to JSON OAuth2 credentials file for access to the Gmail account associated with the target Google Voice number.
- `GOOGLE_SHEETS_CREDENTIALS_PATH`: Path to service account credentials JSON file for the target Google Sheet.

### FAQ
#### Why not Twilio?
Twilio costs money.

#### Why the extra indirection layer with Gmail?
There is no official Google Voice API. Unofficial APIs use the deprecated Google ClientLogin mode of authentication, and it seemed cleaner to me to use an official API with OAuth 2.0 to achieve the intended result. The only downside is that this implementation cannot initiate a SMS conversation i.e. the recipient must have already sent a message to the Voice number.

### License
Released under the MIT License. See [LICENSE.md](https://github.com/katexyu/google-voice-sheets/blob/master/LICENSE.md) for details.