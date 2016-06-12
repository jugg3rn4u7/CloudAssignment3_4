import os
import sys
import json

# dev
connection_properties = {
    'host': 'localhost',
    'port': 3306,
    'user': 'root',
    'passwd': 'root'
}

# prod
# retrieve service params from vcap
# vcap_services = json.loads(os.environ['VCAP_SERVICES'])
# mysql_srv = vcap_services['cleardb'][0]
# cred = mysql_srv['credentials']
# host = cred['hostname']
# port = cred['port']
# name = cred['name']
# database = 'cloud_assignments'
# user = cred['username']
# password = cred['password']

# connection_properties = {
# 	'host': host,
# 	'port': port,
# 	'user': user,
# 	'passwd': password
# }