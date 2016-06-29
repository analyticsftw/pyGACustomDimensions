""" this script extracts a list of custom dimensions in a Google Analytics property 
using the Management API and exports to CSV
"""

import argparse
import config
import csv

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
  service = build(api_name, api_version, http=http)
  return service

def main():
    # Refer to the config.py settings file for credentials
    service_account_email = config.apiSettings['service_account_email']
    key_file_location = config.apiSettings['key_file_location']

    print("Reading custom dimensions from property")
    scope = ['https://www.googleapis.com/auth/analytics.readonly']
    service = get_service('analytics', 'v3', scope, key_file_location, service_account_email)
    
    print("Analyzing available accounts.")
    properties = service.management().webproperties().list(accountId='~all').execute()

    propertiesList = properties.get("items")
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
            dimdump.writerow(["Index","Scope","Name","Active"])
            for dimension in dimList:
                dimdump.writerow([str(dimension["index"]),dimension["scope"],dimension["name"],str(dimension["active"])])
    print ("\nDone.\n")
if __name__ == '__main__':
  main()