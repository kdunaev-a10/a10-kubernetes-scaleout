########################################################################################################################
# Copyright(C) 2007-2014, A10 Networks Inc. All rights reserved.
# Software for all A10 products contain trade secrets and confidential
# information of A10 Networks and its subsidiaries and may not be
# disclosed, copied, reproduced or distributed to anyone outside of
# A10 Networks without prior written consent of A10 Networks, Inc.
########################################################################################################################

import json
import httplib
import optparse


### This part is to specify the command line options ###
# specify device and command file
parser = optparse.OptionParser()
parser.add_option('-d', '--device', dest="device_ip", action="store")
#parser.add_option('-u', '--user', dest="username", action="store")
#parser.add_option('-p', '--password', dest="password", action="store")
#parser.add_option('-n', '--hostname', dest="hostname", action="store")
parser.add_option('-i', '--id', dest="id", action="store")
parser.add_option('-a', '--address', dest="address", action="store")


options, args = parser.parse_args()
VTHUNDERIP = options.device_ip
#ADMIN_USER = options.username
#ADMIN_PASSWORD = options.password
#HOSTNAME = options.hostname
ID = options.id
ADDRESS = options.address

SO_CONFIG = True

class Sdk:
    JSON_INDENT = 4
    AUTH_URI = "/axapi/v3/auth"
    LOGOFF_URI = "/axapi/v3/logoff"
    def __init__(self,
                 host_ip,
                 user_name = "admin",
                 password = "a10",
                 enable_debug = False):
        self.host = host_ip
        self.username = user_name
        self.password = password
        self.enable_debug = enable_debug


    def print_json(self, json_input):
        if self.enable_debug:
            print json.dumps(json_input, indent = self.JSON_INDENT)

    def post(self, uri, payload):
        conn = httplib.HTTPSConnection(self.host)
        json_payload = json.dumps(payload)
        if self.enable_debug:
            print "\nPOST "+ uri + "\nPayload:\n"
        self.print_json(json_input = payload)
        c = conn.request("POST", uri, json_payload, self.headers)
        try:
            conn_response = conn.getresponse()
            json_response = conn_response.read()
            response = json.loads(json_response.replace('\n', ''))
            if self.enable_debug:
                print "HTTP Status Code: %d" % (conn_response.status)
                print "HTTP Reason: %s" % (conn_response.reason)

            if (conn_response.status != 204):
                self.print_json(json_input = response)

            return (conn_response.status, response)
        except Exception as ex:
            raise ex



    def get(self, uri):
        conn = httplib.HTTPSConnection(self.host)
        conn.request("GET", uri, body=None, headers = self.headers)
        if self.enable_debug:
            print "\nGET " + uri
        try:
            response = ""
            conn_response = conn.getresponse()
            json_response = conn_response.read()
            if conn_response.status != 204:
                response = json.loads(json_response.replace('\n', ''))
                if self.enable_debug:
                  print self.print_json(response)
            if self.enable_debug:
                print "HTTP Status Code: %d" % (conn_response.status)
                print "HTTP Reason: %s" % (conn_response.reason)
            return (conn_response.status, response)
        except Exception as ex:
            raise ex


    def put(self, uri, payload):
        conn = httplib.HTTPSConnection(self.host)
        json_payload = json.dumps(payload)
        c = conn.request("PUT", uri, json_payload, self.headers)
        if self.enable_debug:
            print "\nPUT "+ uri + "\nPayload:\n"
        self.print_json(json_input = payload)
        try:
            conn_response = conn.getresponse()
            json_response = conn_response.read()
            response = ""
            if conn_response.status != 204:
                response = json.loads(json_response.replace('\n', ''))
                if self.enable_debug:
                   print self.print_json(response)
            if self.enable_debug:
              print "HTTP Status Code: %d" % (conn_response.status)
              print "HTTP Reason: %s" % (conn_response.reason)
            return (conn_response.status, response)
        except Exception as ex:
            raise ex


    def delete(self, uri):
        conn = httplib.HTTPSConnection(self.host)
        conn.request("DELETE", uri, body = None, headers = self.headers)
        if self.enable_debug:
            print "\nDELETE " + uri
        try:
            conn_response = conn.getresponse()
            json_response = conn_response.read()
            response = ""
            if conn_response.status != 204:
                response = json.loads(json_response.replace('\n', ''))
                if self.enable_debug:
                  print self.print_json(response)
            if self.enable_debug:
                print "HTTP Status Code: %d" % (conn_response.status)
                print "HTTP Reason: %s" % (conn_response.reason)
            return (conn_response.status, response)
        except Exception as ex:
            raise ex



    def logon(self):
        if self.enable_debug:
            print "\n***** LOGON *****"
        json_content_type_header = {'Content-type': 'application/json'}

        conn = httplib.HTTPSConnection(self.host)
        credentials_dict = {}
        credentials_dict["credentials"] = {}
        credentials_dict["credentials"]["username"] = self.username
        credentials_dict["credentials"]["password"] = self.password
        if self.enable_debug:
            print (credentials_dict)

        conn.request("POST", self.AUTH_URI, json.dumps(credentials_dict), json_content_type_header)

        try:
            response = json.loads(conn.getresponse().read())
            if "authresponse" in response:
                signature = str(response['authresponse']['signature'])
                self.headers = {'Content-type': 'application/json', 'Authorization': "A10 %s" % signature}
            else:
                raise Exception("Unable to logon")
        except Exception as ex:
            raise Exception(ex.message)


    def logoff(self):
        if self.enable_debug:
            print "\n***** LOGOFF *****"
        conn = httplib.HTTPSConnection(self.host)
        #conn.request("POST", self.LOGOFF_URI, "", self.headers)
        conn.request("GET", self.LOGOFF_URI, "", headers = self.headers)

        response = conn.getresponse().read()
        return response

    def axapi_failure(result):
        if 'response' in result and result['response'].get('status') == 'fail':
            return True
        return False



if __name__ == "__main__":

    sdk = Sdk(host_ip = VTHUNDERIP)
    sdk.logon()

    try:
      (s,r_so) = sdk.get(uri='/axapi/v3/scaleout/cluster')
      so_cluster = r_so['cluster-list'][0]['cluster-id']
    except Exception as ex:
       print "No Scaleout configuration"
#       SO_CONFIG = False

#    SO_CONFIG = False
    if not SO_CONFIG:
       cluster_config= {
              "cluster-list": [
                {
                  "cluster-id": 1,
                  "local-device": {
                    "action": "enable"
                   },
                }
             ]
         }

#       (s,r)=sdk.put(uri='/axapi/v3/scaleout/cluster', payload=cluster_config)
#       so_cluster = r_so['cluster-list'][0]['cluster-id']
    commands=[];
    commands.append("scaleout "+str(so_cluster))
    commands.append("local-device")
    commands.append("enable")

    cluster_config = {
      "commandList": commands,
    }

    (s,r)=sdk.post(uri='/axapi/v3/clideploy/', payload=cluster_config)


    if s != 200:
       print "ERROR:", s, r

    sdk.logoff()
