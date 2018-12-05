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

# Statuspage.io statuses
OPERATIONAL = 'operational'
DEGRADED_PERFORMANCE = 'degraded_performance'
PARTIAL_OUTAGE = 'partial_outage'
MAJOR_OUTAGE = 'major_outage'
UNDER_MAINTENANCE = 'under_maintenance'


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

class ComponentsList():
    def __init__(self, page_id):
        url = 'https://{0}.statuspage.io/api/v2/components.json'
        self._url = url.format(page_id)
    
    def load(self):
        # request the json from statuspage
        r = requests.get(self._url)
        components_json = r.text
        
        self._data = json.loads(components_json)


    def get_component(self, id):
        component_list = self._data.get('components')
        # print(component_list)
        for c in component_list:
            if c.get('id') == id:
                if c.get('group_id'):
                    parent = self.get_component(c.get('group_id'))
                    parent_name = parent.get('name')
                    full_name = '{0} - {1}'.format(parent_name, c.get('name'))
                    c['name'] = full_name

                return c


def output_result(code, message, longmessage=None):
    # print the status description message
    print(message)

    # print the multi-line long message
    if len(longmessage) > 0:
        print(longmessage)

    # exit process
    raise SystemExit(code)


def main(args):
    #create the result
    result = CheckResult()

    # load the components json
    page_id = args.get('page_id')
    components = ComponentsList(page_id)
    try:
        components.load()
    except JSONDecodeError:
        message = 'UNKNOWN: page {0} not found'.format(page_id)
        result.set_message(message)
        result.set_code(UNKNOWN)
        result.send()

    # find the component
    component_id = args.get('component_id')
    component = components.get_component(component_id)
    
    # return unknown if component not found
    if component is None:
        message = 'UNKNOWN: component {0} not found'.format(component_id)
        result.set_message(message)
        result.set_code(UNKNOWN)
        result.send()
        
    # perform check logic
    status = component.get('status')
    name = component.get('name')

    if status == OPERATIONAL:
        message = 'OK: {0} is {1}'.format(name, status)
        result.set_message(message)
        result.set_code(OK)
    elif status == DEGRADED_PERFORMANCE:
        message = 'WARNING: {0} is {1}'.format(name, status)
        result.set_message(message)
        result.set_code(WARNING)
    elif status == PARTIAL_OUTAGE or status == MAJOR_OUTAGE:
        message = 'CRITICAL: {0} is {1}'.format(name, status)
        result.set_message(message)
        result.set_code(CRITICAL)

    result.send()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='statuspage.io nagios check')
    parser.add_argument('page_id', help='statuspage.io page id')
    parser.add_argument('component_id', help='component id')

    # args = {}
    args = parser.parse_args()
    main(vars(args))
