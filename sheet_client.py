import gspread
import json
from oauth2client.client import SignedJwtAssertionCredentials
import os
import re

class GoogleSheetClient:
    """
    Client that interfaces with the specified Google Sheet.
    """
    def __init__(self, sheet_key, sheet_credentials_path):
        self.worksheet = self._load_spreadsheet(sheet_key, sheet_credentials_path)

    def _load_spreadsheet(self, sheet_key, sheet_credentials_path):
        json_key = json.load(open(sheet_credentials_path))
        scope = ['https://spreadsheets.google.com/feeds']
        credentials = SignedJwtAssertionCredentials(json_key['client_email'], json_key['private_key'], scope)
        gc = gspread.authorize(credentials)
        return gc.open_by_key(sheet_key).sheet1

    def _format_get_response(self, row):
        """
        Define how to format the response message for a get.
        """
        name = row[0]
        count = int(row[1])
        values = '|| ' + ' * * '.join(row[2:count+2]) if count > 0 else ''
        return '%s || \nTotal Count: %d %s' % (name, count, values)

    def _get_matching_row_data(self, row_key):
        """
        Get all rows with the matching row key.
        Returns a list of lists of cells that belong to matching rows.
        """
        row_key = row_key.lower()
        sheet_values = self.worksheet.get_all_values()
        matches = []
        for row in sheet_values:
            if row_key in row[0].lower():
                matches.append(row)
        return matches

    def _get_matching_row_keys(self, row_key):
        """
        Find matching row keys.
        Returns a list of tuples in the format (row_index, row_key).
        """
        row_key = row_key.lower()
        row_keys = self.worksheet.col_values(1)
        matches = []
        for row, val in enumerate(row_keys):
            if not val:
                continue
            if row_key in val.lower():
                matches.append((row+1, val))
        return matches

    def get_data(self, row_key):
        """
        Returns a list of cell values in the row following the key.
        """
        rows = self._get_matching_row_data(row_key)
        if len(rows) == 0:
            return 'Did not find any matches.'
        elif len(rows) > 1:
            keys = ', '.join([r[0] for r in rows])
            return 'There was more than one match: %s' % keys
        else:
            return self._format_get_response(rows[0])

    def add_data(self, row_key, data):
        """
        Add a new entry to the end of the row.
        """
        rows = self._get_matching_row_keys(row_key)
        if len(rows) == 0:
            return 'Did not find any matches.'
        elif len(rows) > 1:
            keys = ', '.join([r[1] for r in rows])
            return 'There was more than one match: %s' % keys
        else:
            num_values = len(self.worksheet.row_values(rows[0][0]))
            self.worksheet.update_cell(rows[0][0], num_values + 1, data)
            return 'Updated %s' % rows[0][1]
