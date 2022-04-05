""" this script extracts a list of custom dimensions in a Google Analytics property 
using the Management API and exports to CSV
"""

import csv
import os.path
import re
import sys
import argparse
from click import prompt
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from urllib.error import HTTPError

# Define the auth scopes to request.
# If modifying these scopes, delete the file token.json.
SCOPES = [
  'https://www.googleapis.com/auth/analytics.readonly',
  'https://www.googleapis.com/auth/analytics.edit'
]

def main():
  cred_file  = "tokens/credentials.json"
  token_file = "tokens/ga_management.json"
  creds = None
  # The file token.json stores the user's access and refresh tokens, and is
  # created automatically when the authorization flow completes for the first
  # time.
  if not os.path.exists(cred_file):
    print ("No credentials file found; create one by visiting the GCP console and creating a new project.\nVisit https://console.cloud.google.com/apis/credentials to create a new OAuth key and save it locally as tokens/credentials.json")
    sys.exit()
  if os.path.exists(token_file):
      creds = Credentials.from_authorized_user_file(token_file, SCOPES)
  # If there are no (valid) credentials available, let the user log in.
  if not creds or not creds.valid:
      if creds and creds.expired and creds.refresh_token:
          creds.refresh(Request())
      else:
          flow = InstalledAppFlow.from_client_secrets_file(
              cred_file, SCOPES)
          creds = flow.run_local_server(port=0)
      # Save the credentials for the next run
      with open(token_file, 'w') as token:
          token.write(creds.to_json())
  # Authenticate and construct service.
  print("Connecting to Google Analytics API for authentication")
  
  service = build('analytics', 'v3', credentials=creds)

  print("Reading custom dimensions from property")
    
  print("Analyzing available accounts.")
  properties = service.management().webproperties().list(accountId='~all').execute()

  propertiesList = properties.get("items")
  nItems = len(propertiesList)
  print("Found "+str(nItems)+" properties.")
  if nItems >30:
    have_time = prompt("This script will take a long time to run. Continue? (y/n)")
    if have_time != "y":
      print("Exiting.")
      sys.exit()
  for property in propertiesList:
      print ("Exporting:\t"+property["id"]+"\t"+property["name"])
      csvname = "exports/"+property["id"] + ".csv"
      pchunks = property["id"].split("-")
      dimensions = service.management().customDimensions().list(
        accountId=pchunks[1],
        webPropertyId=property["id"],
      ).execute()
      dimList = dimensions.get("items")
      with open(csvname, 'w', newline='') as csvfile:
        dimdump = csv.writer(csvfile, delimiter=",")
        #Index,Scope,Name,Active
        dimdump.writerow(["Index","Name","Scope","Active"])
        for dimension in dimList:
          dimdump.writerow([
            str(dimension["index"]),
            dimension["name"],
            dimension["scope"],
            str(dimension["active"])
          ])
  print ("\nDone.\n")
if __name__ == '__main__':
  main()