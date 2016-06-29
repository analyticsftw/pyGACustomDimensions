# pythongoogleanalyticscustomdimensions
This set of Python scripts allows for the mass creation and modification of Google Analytics custom dimensions, using the Management API.
This can be adapted with other API connectors, with Java or Javascript for instance.

Reference:
- Google Analytics Management API (v3): https://developers.google.com/analytics/devguides/config/mgmt/v3/
- Getting started with the Google API Python client: https://developers.google.com/api-client-library/python/start/get_started

Requires:
- A Google Cloud Platform project with a set of credentials and a key (.p12 or JSON, although this project uses .p12).
  - See https://console.cloud.google.com/iam-admin/iam/iam-zero
- A Google Analytics account with access granted to the e-mail address set in the credentials
- Python 3 or higher
- Python module pyOpenSSL
  - https://pypi.python.org/pypi/pyOpenSSL
  - or install using pip: pip install --upgrade pyOpenSSL
- Python Google API client library: 
  - https://pypi.python.org/pypi/google-api-python-client/
  - or install using pip: pip install --upgrade google-api-python-client
