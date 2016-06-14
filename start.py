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
import memcache
from os import walk
from flask import Flask, jsonify, request, redirect
from werkzeug import secure_filename
import pymysql.cursors

VALID_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif','doc','docx','xls', 'csv'])
BASEPATH = os.path.dirname(os.path.abspath(__file__))

app = Flask(__name__) 
app.config['DATA'] = os.path.join(BASEPATH,'data')
app.config['PATH'] = "data"
DB_NAME = 'cloud_assignments'

# DB Connection
from dbsettings import connection_properties
print(connection_properties)
print(app.config['PATH'])

memc = memcache.Client(['127.0.0.1:11211'], debug=1)

def create_schema():
    try:

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
                 cur.execute("DROP DATABASE IF EXISTS `%s`" % DB_NAME)
                 cur.execute("CREATE DATABASE IF NOT EXISTS {} DEFAULT CHARACTER SET 'utf8'".format(DB_NAME))
                 conn.commit()
                 cur.close()
            except Exception as e:
                    print("Exception at line number: {}".format(sys.exc_info()[-1].tb_lineno))
                    print("Exception : %s" % e)

        def create_cache_query_table():
            try:
                    cur = conn.cursor()
                    cur.execute( "CREATE TABLE `%s" % DB_NAME + "`.`CACHED_QUERIES`(id int(11) AUTO_INCREMENT, query varchar(1000), primary key(id))" )
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
                    f = []
                    for (dirpath, dirnames, filenames) in walk(app.config['PATH']):
                         f.extend(filenames)
                         break
                    for i in range(len(f)):
                         filepath = os.path.join( app.config['DATA'], f[i] )
                         (filename, ext) = f[i].split(".")
                         startTime = int(round(time.time() * 1000))
                         command = "sudo mysqlimport --ignore-lines=1 --fields-terminated-by=, --local -u root -proot %s " % DB_NAME + "%s" % filepath
                         print("command : ", command)
                         os.system(command)   
                         endTime = int(round(time.time() * 1000))
                         cur = conn.cursor()
                         conn.commit()
                         cur.close()
                         print("Time taken to import file : ", endTime - startTime,'ms') 
            except Exception as e:
                    print("Exception at line number: {}".format(sys.exc_info()[-1].tb_lineno))
                    print("Exception : %s" % e)

        startTime = int(round(time.time() * 1000))
        create_database()
        statements = read_header()
        for i in range(len(statements)):
    	   create_table(statements[i])
        create_cache_query_table()
        load_data()
        endTime = int(round(time.time() * 1000))
        print("Time taken to load the data into MySQL : ", endTime - startTime,'ms')
        conn.close()

    except Exception as e:
        print("Exception at line number: {}".format(sys.exc_info()[-1].tb_lineno))
        print("Exception : %s" % e)

@app.route("/")
def ShowDefault():
	return app.send_static_file('index.html')

@app.route("/create")
def create():
    try:
         create_schema() 
         return jsonify(results=True)      
    except Exception as e:
        print("Exception at line number: {}".format(sys.exc_info()[-1].tb_lineno))
        print("Exception : %s" % e)
        return jsonify(results=False)    

@app.route("/query", methods=['POST'])
def RunQuery():
	try:
         startTime = int(round(time.time() * 1000))
         query = request.form["query"]
         times = request.form["times"]
         cached = request.form["cached"]
         print("Cached : ", cached.encode("utf-8") == "true")
         print("Query : ", query)
         conn = pymysql.connect(**connection_properties)
         cur = conn.cursor()
         if cached.encode("utf-8") == "true":
            q = "INSERT INTO `%s`.`CACHED_QUERIES`(query) VALUES('%s')" % (DB_NAME, query.encode("utf-8"))
            print("Inside : ", q)
            cur.execute(q)
            conn.commit()
	 q = "SELECT MAX(id) FROM `%s`.`CACHED_QUERIES`" % DB_NAME
         cur.execute(q)
         row = cur.fetchone()
         _id = row[0]
         for i in range(int(times.encode("utf-8"))):
            cur.execute(query)
         if cached.encode("utf-8") is "true":
            cur.execute(query)
            rows = cur.fetchall()
            memc.set('{}'.format(_id), rows, 60)
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

@app.route("/cquery", methods=['POST'])
def RunCachedQuery():
    try:
         startTime = int(round(time.time() * 1000))
         _id = request.form["id"]
         times = request.form["times"]
         print(_id.encode("utf-8"))
         print "Loaded data from memcached"
         for i in range(int(times.encode("utf-8"))):
            cached_data = memc.get("{}".format(_id.encode("utf-8")))
         endTime = int(round(time.time() * 1000))
         print("Time to execute get results from cache : ", endTime - startTime,'ms')
         data = { "time_elapsed": (endTime - startTime) }
         return jsonify(results=data)
    except Exception as e:
        print("Exception at line: {}".format(sys.exc_info()[-1].tb_lineno))
        print("Exception: %s" % e)
        data = { "time_elapsed": "Check your query. Error in measuring time" }
        return jsonify(results=data)

@app.route("/insert_query", methods=['POST'])
def RunInsertQuery():
    try:
         startTime = int(round(time.time() * 1000))
         query = request.form["query"]
         times = request.form["times"]
         print("Query : ", query)
         conn = pymysql.connect(**connection_properties)
         cur = conn.cursor()
         for i in range(int(times.encode("utf-8"))):
            cur.execute(query)
            conn.commit()
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

@app.route("/getQueries")
def GetCachedQueries():
        try:
                conn = pymysql.connect(**connection_properties)
                cur = conn.cursor()
        	q = "SELECT * FROM `%s`.`CACHED_QUERIES`" % DB_NAME
        	print(q)
                cur.execute(q)
                rows_count = cur.rowcount
                rowarray_list = []
                if rows_count > 0:
                    rows = cur.fetchall()
                    for i in range(len(rows)):
                        t = (rows[i][0], rows[i][1])
                        rowarray_list.append(t)
                    print(rowarray_list)
                    j = json.dumps(rowarray_list)
                    cur.close()
                    conn.close()
                    return j
                else:
                    j = []
                    return jsonify(results=j)
        except Exception as e:
                print("Exception at line number: {}".format(sys.exc_info()[-1].tb_lineno))
                print("Exception : %s" % e)
                j = []
                return jsonify(results=j)

@app.route('/upload_file', methods=['GET', 'POST'])
def UploadFile():
    try:
        startTime = int(round(time.time() * 1000))
        if request.method == 'POST':
            local_file = request.files['generic_file']
            filename = secure_filename(local_file.filename)
            local_file.save(os.path.join(app.config['DATA'], filename))
            issue_permissions = "sudo chmod -R 777 %s" % os.path.join(app.config['DATA'], filename)
            os.system(issue_permissions)
        endTime = int(round(time.time() * 1000))
        print("Time to upload the file : ", endTime - startTime,'ms')
        return app.send_static_file('index.html')            
    except Exception as e:
        print("Exception at line number: {}".format(sys.exc_info()[-1].tb_lineno))
        print e
        return app.send_static_file('index.html')
         
port = os.getenv('PORT', '8000')
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(port))