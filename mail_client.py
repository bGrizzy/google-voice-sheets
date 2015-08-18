from apiclient import discovery
from apiclient.http import BatchHttpRequest
import base64
import email
import httplib2
from email.mime.text import MIMEText
import oauth2client

class GoogleMailClient:
    """
    Class that interfaces with Gmail (and by extension, Google Voice)
    """
    GOOGLE_VOICE_DOMAIN = 'txt.voice.google.com'

    def __init__(self, from_email_address, mail_creds_path):
        store = oauth2client.file.Storage(mail_creds_path)
        credentials = store.get()
        http = credentials.authorize(httplib2.Http())

        self.service = discovery.build('gmail', 'v1', http=http)
        self.from_email_address = from_email_address

    def _get_from_header(self, headers):
        """
        Returns the From header value from a list of header objects.
        """
        for h in headers:
            if h['name'] == 'From':
                return h['value']

    def _create_response_message(self, content, recipient):
        """
        Generate a response email object.
        """
        message = MIMEText(content)
        message['to'] = recipient
        message['from'] = self.from_email_address
        message['subject'] = 'Response' # This doesn't matter
        return {'raw': base64.b64encode(message.as_string())}

    def get_unread_emails(self):
        """
        Returns a list of unread emails.
        """
        response = self.service.users().messages().list(userId='me', q='label:unread').execute()
        unread = []
        if 'messages' in response:
            unread.extend(response['messages'])
        return unread

    def handle_unread_emails(self, handle_message):
        """
        Gets unread emails and responds to them accordingly.
        """
        unread = self.get_unread_emails()
        if len(unread) == 0:
            return
        for m in unread:
            message = self.service.users().messages().get(userId='me', id=m['id']).execute()
            snippet = message['snippet'].strip()
            print 'Message snippet: %s' % message['snippet']
            sender = self._get_from_header(message['payload']['headers'])
            print sender

            batch = BatchHttpRequest()
            # Only respond to Google Voice emails.
            if self.GOOGLE_VOICE_DOMAIN in sender:
                result = handle_message(snippet)

                response_message = self._create_response_message(result, sender)
                batch.add(self.service.users().messages().send(userId='me', body=response_message))

            # Remove from unread
            (batch.add(self.service
                           .users()
                           .messages()
                           .modify(userId='me', id=m['id'], body={'removeLabelIds': ['UNREAD']})))
            batch.execute()
