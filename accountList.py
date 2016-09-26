""" A simple example of how to access the Google Analytics Management API 
and pull the list of accounts your email address can access.

Can be adapted to pull a CSV list of all property IDs.
"""
__author__      = "Julien Coquet"
__copyright__   = "Copyright 2016, MIT License"

import argparse
import csv
import config

from apiclient.discovery import build
from oauth2client.service_account import ServiceAccountCredentials

import httplib2
from oauth2client import client
from oauth2client import file
from oauth2client import tools
from six.moves import range

def get_service(api_name, api_version, scope, key_file_location,
                service_account_email):
  """Get a service that communicates to a Google API.

  Args:
    api_name: The name of the api to connect to.
    api_version: The api version to connect to.
    scope: A list auth scopes to authorize for the application.
    key_file_location: The path to a valid service account p12 key file.
    service_account_email: The service account email address.

  Returns:
    A service that is connected to the specified API.
  """

  credentials = ServiceAccountCredentials.from_p12_keyfile(
    service_account_email, key_file_location, scopes=scope)

  http = credentials.authorize(httplib2.Http())

  # Build the Google API service object.
  service = build(api_name, api_version, http=http)

  return service

def main():
  # Define the auth scopes to request.
  scope = ['https://www.googleapis.com/auth/analytics.readonly']

  # Refer to the config.py settings file for credentials
  service_account_email = config.apiSettings['service_account_email']
  key_file_location = config.apiSettings['key_file_location']

  # Authenticate and construct service.
  print("Connecting to Google Analytics API for authentication")
  service = get_service('analytics', 'v3', scope, key_file_location, service_account_email)

  print("Pulling available accounts")
  accounts = service.management().accounts().list().execute().get("items")
  for account in accounts:
      properties = service.management().webproperties().list(accountId=account["id"]).execute()
      propertiesList = properties.get("items")
      for property in propertiesList:
          print (account["name"]+","+account["id"]+","+property["id"]+","+property["name"])

if __name__ == '__main__':
  main()
