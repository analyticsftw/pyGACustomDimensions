""" Filling a Google Analytics property with custom dimensions using the Management API."""

import argparse
import config
import csv
import sys
import time

from apiclient.discovery import build
from oauth2client.service_account import ServiceAccountCredentials

import httplib2
from oauth2client import client
from oauth2client import file
from oauth2client import tools
from six.moves import range

def get_service(api_name, api_version, scope, key_file_location, service_account_email):

  credentials = ServiceAccountCredentials.from_p12_keyfile(service_account_email, key_file_location, scopes=scope)
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
  # Define the auth scopes to request.
  scope = ['https://www.googleapis.com/auth/analytics.readonly']

  # Refer to the config.py settings file for credentials
  service_account_email = config.apiSettings['service_account_email']
  key_file_location = config.apiSettings['key_file_location']
  
  propertyId = input('Enter the property ID (in the format UA-XXXXXXXX-Y): ')
  accountBits = propertyId.split('-')
  accountId = accountBits[1]
  isPremium = input('Is this a Premium property? (y/n): ')
  dimRange = 200 if isPremium == "y" else 20
  isActive = input('Leave all custom dimensions active? (y/n): ')
  dimActive = True if (isActive == "y") else False
  isType = input('Default dimension scope? (HIT, SESSION, USER, PRODUCT): ')
  
  # Authenticate and construct service.
  print("Connecting to Google Analytics API for authentication")
  service = get_service('analytics', 'v3', scope, key_file_location, service_account_email)

  print("Pulling dimensions")
  dimensions = service.management().customDimensions().list(
    accountId=accountId,
    webPropertyId=propertyId
  ).execute()
  
  time.sleep(10)  
  nbDims = dimensions.get("totalResults")
  print("Found " + str(nbDims) + " custom dims")
  if nbDims < dimRange+1:
      nbNewDims = dimRange - nbDims
      print("Creating " + str(nbNewDims) + " custom dimensions")
      scope = ['https://www.googleapis.com/auth/analytics.edit']
      service = get_service('analytics', 'v3', scope, key_file_location, service_account_email)
      
      for i in range(nbDims+1,dimRange)
          newDim = service.management().customDimensions().insert(
            accountId=accountID,
            webPropertyId=propertyId,
            body={
                'name':"Spare custom dimension #"+ str(i),
                'scope': isType,
                'active': dimActive
            }            
          ).execute()
          if i %10 == 0:
              time.sleep(10)
          progress(i,nbNewDims)
      print "\n\nDone."
if __name__ == '__main__':
  main()
