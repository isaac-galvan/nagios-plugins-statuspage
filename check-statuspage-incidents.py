#!/usr/bin/env python3
#
# Author: Isaac J. Galvan
# Date: 2018-12-04
#
# https://github.com/

import argparse
import datetime
import json
import requests
from json.decoder import JSONDecodeError

# Nagios return codes
OK = 0
WARNING = 1
CRITICAL = 2
UNKNOWN = 3

# Statuspage.io unresolved incident statuses
INVESTIGATING = 'investigating'
IDENTIFIED = 'identified'
MONITORING = 'monitoring'

class CheckResult():
    def __init__(self):
        self._exitcode = UNKNOWN
        self._message = ''
        self._longmessage = ''
    
    def set_code(self, code):
        self._exitcode = code
    
    def set_message(self, message):
        self._message = message

    def set_longmessage(self, longmessage):
        self._longmessage = longmessage

    def send(self):
        # print the status description message
        print(self._message)

        # print the multi-line long message
        if len(self._longmessage) > 0:
            print(self._longmessage)

        # exit process
        raise SystemExit(self._exitcode)

class IncidentList():
    def __init__(self, page_id):
        url = 'https://{0}.statuspage.io/api/v2/incidents/unresolved.json'
        self._url = url.format(page_id)
        self._load()

    def _load(self):
        #request the json from statuspage
        r = requests.get(self._url)
        incidents_json = r.text
        self._data = json.loads(incidents_json)

    def get_incident_count(self):
        return len(self._data.get('incidents'))

    def get_incident_summary(self):
        summary = ''
        incidents = self._data.get('incidents')
        for i in incidents:
            summary += '{2}: {1} ({0})\n'.format(i.get('shortlink'), i.get('name'), i.get('status').capitalize())
        return summary

def main(args):
    # create the result
    result = CheckResult()

    # load the unresolved incidents json
    page_id = args.get('page_id')
    try:
        incidents = IncidentList(page_id)
    except:
        result.set_code(UNKNOWN)
        result.set_message('UNKNOWN: Could not load incidents for page {0}'.format(page_id))
        result.send()

    # perform check login
    count = incidents.get_incident_count()
    if count == 0:
        result.set_code(OK)
        result.set_message('OK: No unresolved incidents')
    elif count > 0:
        result.set_code(CRITICAL)
        result.set_message('CRITICAL: {0} unresolved incidents(s) reported'.format(count))
        result.set_longmessage(incidents.get_incident_summary())
    result.send()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='statuspage.io nagios check')
    parser.add_argument('page_id', help='statuspage.io page id', default='208q92hckwws')

    args = parser.parse_args()
    main(vars(args))