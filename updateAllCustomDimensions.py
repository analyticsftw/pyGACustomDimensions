""" Fills up your Google Analytics property with custom dimensions """

import csv
import os.path
import re
import sys
import argparse
import time
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

  
  propertyId = input('Enter the property ID (in the format UA-XXXXXXXX-Y): ')
  if "UA-" not in propertyId:
    print("Invalid property ID. Please try again with a property ID in the format UA-XXXXXXXX-YY.")
    sys.exit()
  
  accountBits = propertyId.split('-')
  accountId = accountBits[1]
  isPremium = input('Is this a Premium property? (y/n): ')
  if isPremium == '': isPremium = 'n'
  dimRange = 200 if isPremium == "y" else 20
  isActive = input('Leave all custom dimensions active? (y/n): ')
  dimActive = True if (isActive == "y") else False
  isType = input('Default dimension scope? (HIT, SESSION, USER, PRODUCT): ')
  if isType == '': isType = 'HIT'

  # Authenticate and construct service.
  print("Connecting to Google Analytics API for authentication")
  service = build('analytics', 'v3', credentials=creds)
  
  print("Pulling dimensions")
  dimensions = service.management().customDimensions().list(
    accountId=accountId,
    webPropertyId=propertyId
  ).execute()
  
  time.sleep(1)  
  nbDims = dimensions.get("totalResults")
  print("Found " + str(nbDims) + " custom dims")
  print("Updating custom dimensions")
  for i in range(1,dimRange+1):
      # print("Deactivating custom dimension #"+ str(i))
      try:
        newDim = service.management().customDimensions().update(
          accountId=accountId,
          webPropertyId=propertyId,
          customDimensionId="ga:dimension" + str(i),
          body={
              'name':'Custom dimension #'+ str(i),
              'active': dimActive,
              'scope': isType
          }            
        ).execute()
      except HTTPError as err: 
        print("Error for property %s : %s " % (propertyId, err))
      ''' Account for API quotas and pause every so often'''
      if i %10 == 0:
          time.sleep(5)
      progress(i,dimRange+1)
  print ("\n\nDone.")
if __name__ == '__main__':
  main()
