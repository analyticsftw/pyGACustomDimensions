"""
    This script updates a Google Analytics property with custom dimension definitions
    imported from a CSV file
"""


import csv, os, sys

from apiclient.discovery import build
from oauth2client.service_account import ServiceAccountCredentials

import httplib2
from oauth2client import client
from oauth2client import file
from oauth2client import tools


# Settings
import config


def get_service(api_name, api_version, scope, key_file_location, service_account_email):
    #credentials = ServiceAccountCredentials.from_p12_keyfile(
    # service_account_email, key_file_location, scopes=scope
    # )
    credentials = ServiceAccountCredentials.from_json_keyfile_name(
      key_file_location, scopes=scope
    )
    http = credentials.authorize(httplib2.Http())
    # Build the Google API service object.
    service = build(api_name, api_version, http=http)
    return service


def progress(count, total, suffix=''):
    bar_len = 60
    filled_len = int(round(bar_len * count / float(total)))

    percents = round(100.0 * count / float(total), 1)
    bar = '=' * filled_len + '-' * (bar_len - filled_len)

    sys.stdout.write('[%s] %s%s ...%s\r' % (bar, percents, '%', suffix))
    sys.stdout.flush()


def main():
    # Refer to the config.py settings file for credentials
    service_account_email = config.apiSettings['service_account_email']
    key_file_location = config.apiSettings['key_file_location']
    source_csv = input('Enter the path and filename of the CSV template (e.g. ./inputs/cdim.csv): ')
    if not os.path.isfile(source_csv):
      print("File " + source_csv + " not found. Exiting.")
      exit()
    propertyId = input('Enter the property ID (in the format UA-XXXXXXXX-Y): ')
    if not propertyId:
      print("You forgot to enter a GA property ID. Start again.")
      exit()
    separator = input('Which separator are you using in the CSV file? (,/;): ')
    if not separator:
      print("No separator specified. Defaulting to ','")
      separator = ','
    # Break down the UA ID into chunks
    account_bits = propertyId.split('-')
    accountId = account_bits[1]
    import re
    pattern = re.compile("^[0-9]+$")
    match = pattern.search(accountId)
    if not match:
      print("Your account ID (" + accountId + ") does not seem valid")
      exit()
    print("Updating custom dimensions from CSV")
    scope = ['https://www.googleapis.com/auth/analytics.edit']
    service = get_service('analytics', 'v3', scope, key_file_location, service_account_email)
    with open(source_csv) as csvfile:
      # Get the number of lines in the CSV
      num_line = len(csvfile.readlines())
      csvfile.seek(0)
      myreader = csv.reader(csvfile, delimiter=separator)
      # Skip the header
      next(myreader)
      i = 0
      for row in myreader:
        customDimensionId = ("ga:dimension" + str(row[0]))
        # Send Google Analytics Management API call to update the custom dimension from CSV row
        new_dim = service.management().customDimensions().update(
          accountId=accountId,
          webPropertyId=propertyId,
          customDimensionId= customDimensionId,
          body={
            'name':row[1],
            'scope':row[2],
            'active': row[3]
          }       
        ).execute()
        # Update progress bar (purely cosmetic)
        progress(i,num_line)
        i += 1
      print ("\n\nDone.")


if __name__ == '__main__':
  main()
