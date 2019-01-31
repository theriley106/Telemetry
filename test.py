import os
import sys
import json
import requests
import socket
import time
from requests.auth import HTTPBasicAuth

GATEWAY_URL = "https://gateway-staging.ncrcloud.com"

# authentication used for NCR API
auth = HTTPBasicAuth('acct:telemetry@telemetryserviceuser', 'passmord')
headers = {
    'nep-application-key': '8a0084a165d712fd016692b1b0840070',
    'nep-organization': 'ncr-market',
    'nep-service-version': '2.2.1:2'
}
catalog = None

def get_catalog():
    # Connecting to the API and returning the entire catalog avaiable
    r = requests.get(GATEWAY_URL + "/ias/1/item-availability/1/", auth=auth, headers=headers)
    print r.json()

get_catalog()
