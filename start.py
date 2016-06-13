# Copyright 2015 IBM Corp. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
import sys
import time
import json
from os import walk
from flask import Flask, jsonify, request, redirect
from werkzeug import secure_filename
import pymysql.cursors

BASEPATH = os.path.dirname(os.path.abspath(__file__))

app = Flask(__name__) 
app.config['DATA'] = os.path.join(BASEPATH,os.path.join('static','data'))
app.config['PATH'] = "data"

# DB Connection
from dbsettings import connection_properties
print(connection_properties)
print(app.config['PATH'])

try:
	
    DB_NAME = 'cloud_assignments'

    def clean_str(string):
	return string.strip("\r") 
	
    def create_statement(table_name, attributes):
	statement = "create table `%s`" % DB_NAME + ".`%s`" % ( table_name ) + "("
        attr_string = "" 
	for i in range(len(attributes)):
		attr_string += clean_str( attributes[i] ) + " varchar(100),"
	attr_string = attr_string[:-1]
	#print("Attr str : ", attr_string)
	statement += attr_string
	statement += ");"
	return statement

    def read_header():
	try:
		f = []
		statements = []
		for (dirpath, dirnames, filenames) in walk(app.config['PATH']):
            		f.extend(filenames)
            		break
		print("Files : ", f)
		for i in range(len(f)):
			filepath = os.path.join( app.config['PATH'], f[i] )
			(filename, ext) = f[i].split(".")
                	content = []
                	with open(filepath, 'rb') as f:
                    		content = [x.strip('\n') for x in f.readlines()]
			columns = content[0].split(",")                    		
			#print("columns: ", columns)
			statements.append( create_statement(filename, columns) )		
		#for i in range(len(statements)):
			#print("Table {}".format(i))
			#print(statements[i])
		return statements

	except Exception as e:
	    print("Exception at line number: {}".format(sys.exc_info()[-1].tb_lineno))
            print("Exception : %s" % e)

    conn = pymysql.connect(**connection_properties)

    def create_database():
        try:
                cur = conn.cursor()
		cur.execute(
                    "DROP DATABASE IF EXISTS {}".format(DB_NAME))
                cur.execute(
                    "CREATE DATABASE IF NOT EXISTS {} DEFAULT CHARACTER SET 'utf8'".format(DB_NAME))
                conn.commit()
                cur.close()

        except Exception as e:
            print("Exception at line number: {}".format(sys.exc_info()[-1].tb_lineno))
            print("Exception : %s" % e)

    def create_table(statement):
        try:
                cur = conn.cursor()
                cur.execute( statement )
                conn.commit()
                cur.close()
        except Exception as e:
            print("Exception at line number: {}".format(sys.exc_info()[-1].tb_lineno))
            print("Exception : %s" % e)

    def load_data():
        try:
        		cur = conn.cursor()
        		f = []
                for (dirpath, dirnames, filenames) in walk(app.config['PATH']):
                        f.extend(filenames)
                        break
                for i in range(len(f)):
                        filepath = os.path.join( app.config['DATA'], f[i] )
                        (filename, ext) = f[i].split(".")
    			cur.execute("LOAD DATA LOCAL INFILE '%s'" % filepath +
    				    "INTO TABLE %s" % ("`"+ DB_NAME  +"`.`" + filename +"`") + 
    				    "FIELDS TERMINATED BY ','" 
    				    "ENCLOSED BY '\"'" +
    				    "LINES TERMINATED BY '\n'" +
    			 	    "IGNORE 1 ROWS")
    			conn.commit()
                cur.close()
        except Exception as e:
            print("Exception at line number: {}".format(sys.exc_info()[-1].tb_lineno))
            print("Exception : %s" % e)

    startTime = int(round(time.time() * 1000))
    create_database()
    statements = read_header()
    for i in range(len(statements)):
	create_table(statements[i])
    #load_data()
    endTime = int(round(time.time() * 1000))
    print("Time taken to load the data into MySQL : ", endTime - startTime,'ms')
    conn.close()

except Exception as e:
    print("Exception at line number: {}".format(sys.exc_info()[-1].tb_lineno))
    print("Exception : %s" % e)

@app.route("/")
def ShowDefault():
	return app.send_static_file('index.html')

@app.route("/query", methods=['POST'])
def RunQuery():
	try:
         startTime = int(round(time.time() * 1000))
         query = request.form["query"]
         times = request.form["times"]
         print(query.encode("utf-8"))
         conn = pymysql.connect(**connection_properties)
         cur = conn.cursor()
         for i in range(len(times)):
            cur.execute(query)
         cur.close()
         conn.close()
         endTime = int(round(time.time() * 1000))
         print("Time to execute the query : ", endTime - startTime,'ms')
         data = { "time_elapsed": (endTime - startTime) }
         return jsonify(results=data)
	except Exception as e:
		print("Exception at line: {}".format(sys.exc_info()[-1].tb_lineno))
		print("Exception: %s" % e)
        data = { "time_elapsed": "Check your query. Error in measuring time" }
        return jsonify(results=data)
         
port = os.getenv('PORT', '8000')
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(port))