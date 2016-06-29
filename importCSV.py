""" 
    This script updates a Google Analytics property with custom dimension definitions 
    imported from a CSV file
"""

import argparse
import config
import csv
import sys

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
    # Refer to the config.py settings file for credentials
    service_account_email = config.apiSettings['service_account_email']
    key_file_location = config.apiSettings['key_file_location']
    sourceCSV = 'inputs/cdims20.csv'
    propertyId = input('Enter the property ID (in the format UA-XXXXXXXX-Y): ')
    separator = input('Which separator are you using in the CSV file? (,/;): ')
    accountBits = propertyId.split('-')
    accountId = accountBits[1]
    
    print("Updating custom dimensions from CSV")
    scope = ['https://www.googleapis.com/auth/analytics.edit']
    service = get_service('analytics', 'v3', scope, key_file_location, service_account_email)
    
    with open(sourceCSV) as csvfile:
        numline = len(csvfile.readlines())
        csvfile.seek(0)
        myreader = csv.reader(csvfile, delimiter=separator)
        
        next(myreader)
        i = 0
        for row in myreader:
            customDimensionId = ("ga:dimension" + str(row[0]))
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
            progress(i,numline)
            i += 1
        print ("\n\nDone.")
if __name__ == '__main__':
  main()