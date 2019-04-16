# encoding = utf-8

import os
import sys
import time
import datetime
import json
from requests import Session
from requests.auth import HTTPBasicAuth
from xml.etree import ElementTree
from zeep import Client
from zeep.transports import Transport
from xmljson import yahoo

'''
    IMPORTANT
    Edit only the validate_input and collect_events functions.
    Do not edit any other part in this file.
    This file is generated only once when creating the modular input.
'''
'''
# For advanced users, if you want to create single instance mod input, uncomment this method.
def use_single_instance_mode():
    return True
'''

def validate_input(helper, definition):
    """Implement your own validation logic to validate the input stanza configurations"""
    # This example accesses the modular input variable
    # skybox_uri = definition.parameters.get('skybox_uri', None)
    # global_account = definition.parameters.get('global_account', None)
    pass

def collect_events(helper, ew):

    opt_skybox_uri = helper.get_arg('skybox_uri')
    opt_global_account = helper.get_arg('global_account')

    session = Session()
    session.verify = False
    session.auth = HTTPBasicAuth(opt_global_account["username"],opt_global_account["password"])
    transport = Transport(session=session)
    # TODO: research using CachingClient()
    helper.log_info("Trying to connect to %s/skybox/webservice/jaxws/network?wsdl" % opt_skybox_uri)
    try:
        networkclient = Client('%s/skybox/webservice/jaxws/network?wsdl' % opt_skybox_uri, transport=transport)
    except Exception, e:
        helper.log_error("Error connecting to %s with %s" % (opt_skybox_uri, e))
        exit(1)
    else:
        helper.log_info("Successfully connected to %s/skybox/webservice/jaxws/network?wsdl" % opt_skybox_uri)
    with networkclient.settings(raw_response=True):
        #
        # call testService(1) method
        #
        response = networkclient.service.testService('123')
        if response.status_code == 200:
            root = ElementTree.fromstring(response.content)
            data = root.findall('.//return')
            tmp = yahoo.data(data[0])
            if (tmp['return'] != '123'):
                helper.log_error("FATAL ERROR testService(123) didn't return 123")
                exit(1)
        else:
            helper.log_error("FATAL ERROR calling testService() method, status_code %s" % response.status_code)
            exit(1)
        #
        # call countAssetsByNames() method
        #
        response = networkclient.service.countAssetsByNames('*')
        if response.status_code == 200:
            root = ElementTree.fromstring(response.content)
            data = root.findall('.//return')
            tmp = yahoo.data(data[0])
            assetcount = tmp['return']
        else:
            helper.log_error("FATAL ERROR calling countAssetsByNames() method, status_code %s" % response.status_code)
            exit(1)
        #
        # call findAssetsByNames() method
        #
        subrange_type = networkclient.get_type('ns0:subRange')
        subrange = subrange_type(start=0,size=assetcount)
        response = networkclient.service.findAssetsByNames('*', subrange)
        if response.status_code == 200:
            root = ElementTree.fromstring(response.content)
            assets = root.findall('.//return/assets')
            for asset in assets:
                 tmp = yahoo.data(asset)
                 line = json.dumps(tmp['assets'], indent=2)
                 event = helper.new_event(line, time=None, host=None, index=helper.get_output_index(),
                                              source=None, sourcetype=helper.get_sourcetype(),
                                              done=True, unbroken=True)
                 ew.write_event(event)
        else:
            helper.log_error("FATAL ERROR calling findAssetsByNames() method, status_code %s" % response.status_code)
            exit(1)
