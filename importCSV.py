"""
    This script updates a Google Analytics property with custom dimension definitions
    imported from a CSV file
"""

import csv
import os.path
import re
import sys
import argparse
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from urllib.error import HTTPError

SCOPES = [
  'https://www.googleapis.com/auth/analytics.readonly',
  'https://www.googleapis.com/auth/analytics.edit'
]

def progress(count, total, suffix=''):
    bar_len = 60
    filled_len = int(round(bar_len * count / float(total)))

    percents = round(100.0 * count / float(total), 1)
    bar = '=' * filled_len + '-' * (bar_len - filled_len)

    sys.stdout.write('[%s] %s%s ...%s\r' % (bar, percents, '%', suffix))
    sys.stdout.flush()


def main():
  
  cred_file  = "tokens/credentials.json"
  token_file = "tokens/ga_management.json"
  creds = None
  # The file token.json stores the user's access and refresh tokens, and is
  # created automatically when the authorization flow completes for the first
  # time.
  if os.path.exists(cred_file):
    print ("No credentials file found; create one by visiting the GCP console and creating a new project.\nVisit https://console.cloud.google.com/apis/credentials to create a new OAuth key and save it locally as tokens/credentials.json")
    sys.exit()
  if os.path.exists(token_file):
    creds = Credentials.from_authorized_user_file(token_file, SCOPES)
    print ("we have creds")
  # If there are no (valid) credentials available, let the user log in.
  if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
      creds.refresh(Request())
    else:
      flow = InstalledAppFlow.from_client_secrets_file(cred_file, SCOPES)
      creds = flow.run_local_server(port=0)
      # Save the credentials for the next run
    with open(token_file, 'w') as token:
      token.write(creds.to_json())

  # Authenticate and construct service.
  print("Connecting to Google Analytics API for authentication")
  service = build('analytics', 'v3', credentials=creds)

  sourceCSV = input('Enter the path and filename of the CSV template (e.g. ./inputs/cdim.csv): ')
  if not os.path.isfile(sourceCSV):
    print("File not found: " + sourceCSV)
    sys.exit()
  propertyId = input('Enter the property ID (in the format UA-XXXXXXXX-YY): ')
  if "UA-" not in propertyId:
    print("Invalid property ID. Please try again with a property ID in the format UA-XXXXXXXX-YY.")
    sys.exit()
  separator = input('Which separator are you using in the CSV file? (,/;): ')
  if separator == "":
    separator = ","
    print ("Using default separator: " + separator)
  accountBits = propertyId.split('-')
  accountId = accountBits[1]
  print("Updating custom dimensions from CSV")
  with open(sourceCSV) as csvfile:
    numline = len(csvfile.readlines())
    csvfile.seek(0)
    myreader = csv.reader(csvfile, delimiter=separator)
    next(myreader)
    i = 0
    for row in myreader:
      customDimensionId = ("ga:dimension" + str(row[0]))
      try:
        newDim = service.management().customDimensions().update(
          accountId=accountId,
          webPropertyId=propertyId,
          customDimensionId= customDimensionId,
          body={
            'name':row[1],
            'scope':row[2],
            'active': row[3]
          }       
        ).execute()
      except HTTPError as err:
        print("Error for property %s : %s " % (propertyId, err))
      progress(i,numline)
      i += 1
    print ("\n\nDone.")
 
if __name__ == '__main__':
  main()