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


UPLOAD_FOLDER = os.path.dirname(os.path.abspath(__file__))
VALID_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif','doc','docx','xls', 'org'])

app = Flask(__name__)

BASEPATH = os.path.dirname(os.path.abspath(__file__))
VALID_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif','doc','docx','xls'])

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = os.path.join(BASEPATH, os.path.join('static','files')) 
app.config['TEMP_FOLDER'] = os.path.join(BASEPATH,os.path.join('static','temp'))  

app.config['USERNAME'] = ""
app.config['PASSWORD'] = ""
app.config['USERS'] = os.path.join(BASEPATH,os.path.join('static','users')) 

# DB Connection
from dbsettings import connection_properties
print(connection_properties)
try:
    conn = pymysql.connect(**connection_properties)
    #conn = pymysql.connect(host='%s' % host, port=port, user='%s' % user, passwd='%s' % password, db='%s' % database)

    DB_NAME = 'cloud_assignments'

    def create_database():
        try:
                cur = conn.cursor()
                cur.execute(
                    "CREATE DATABASE IF NOT EXISTS {} DEFAULT CHARACTER SET 'utf8'".format(DB_NAME))
                conn.commit()
                cur.close()
                create_tables()
        except Exception as e:
            print("Exception at line number: {}".format(sys.exc_info()[-1].tb_lineno))
            print("Exception : %s" % e)

    def create_tables():
        try:
                cur = conn.cursor()
                cur.execute("DROP TABLE IF EXISTS `cloud_assignments`.`user`")
                cur.execute("DROP TABLE IF EXISTS `cloud_assignments`.`file_uploads_metadata`")
                cur.execute("CREATE TABLE IF NOT EXISTS `cloud_assignments`.`user` (" +
                            "  `id` int(11) NOT NULL AUTO_INCREMENT," +
                            "  `username` varchar(100) NOT NULL DEFAULT 'user'," +
                            "  `password` varchar(100) NOT NULL DEFAULT 'user'," +
                            "  `file_quota` int(11) NOT NULL," +
                            "  `total_quota` int(11) NOT NULL," +
                            "  PRIMARY KEY (`id`)" +
                            ") ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci")
                cur.execute("CREATE TABLE IF NOT EXISTS `cloud_assignments`.`file_uploads_metadata` (" +
                            "  `file_id` int(11) NOT NULL AUTO_INCREMENT," +
                            "  `file_name` varchar(100) NOT NULL," +
                            "  `file_desc` varchar(250)," +
                            "  `local_file_name` varchar(100) NOT NULL," +
                            "  `file_data` varchar(1000) NOT NULL, " +
                            "  `status` int(11) NOT NULL DEFAULT 1, " +
                            "   `user_id` int(11) NOT NULL REFERENCES user(id), " +
                            "  PRIMARY KEY (`file_id`)" +
                            ") ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci")
                conn.commit()
                cur.close()
                seed_data()
        except Exception as e:
            print("Exception at line number: {}".format(sys.exc_info()[-1].tb_lineno))
            print("Exception : %s" % e)

    def seed_data():
        try:
                filepath = app.config['USERS'] + "/users"
                cur = conn.cursor()
                content = []
                with open(filepath, 'rb') as f:
                    content = [x.strip('\n') for x in f.readlines()]
                    print(content)
                for i in range(len(content)):
                    cur.execute("INSERT INTO `cloud_assignments`.`user`(username, password, file_quota, total_quota) VALUES(" +
                                "  '%s'," % content[i].split(",")[0] +
                                "  '%s'," % content[i].split(",")[1] +
                                "  1048576," +
                                "  10485760" +
                                ")")
                    conn.commit()
                cur.close()
        except Exception as e:
            print("Exception at line number: {}".format(sys.exc_info()[-1].tb_lineno))
            print("Exception : %s" % e)

    create_database()

    conn.close()

except Exception as e:
    print("Exception at line number: {}".format(sys.exc_info()[-1].tb_lineno))
    print("Exception : %s" % e)


@app.route('/')
def Drop():
    return app.send_static_file('index.html')

@app.route('/')
def Main():
    return app.send_static_file('index.html')

def valid_file_ext(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in VALID_EXTENSIONS

@app.route('/authenticate/username/<uname>/password/<pwd>')
#@app.route('/authenticate/username/<uname>')
def Authenticate(uname, pwd):
    try:
        print("username : " + uname)
        print("password : " + pwd)
        data = { "login" : True }
        app.config['USERNAME'] = uname
        app.config['PASSWORD'] = pwd
        app.config['UPLOAD_FOLDER'] = os.path.join(UPLOAD_FOLDER, os.path.join('static','%s' % uname)) 
        print(app.config['UPLOAD_FOLDER'])
        conn = pymysql.connect(**connection_properties)
        cur = conn.cursor()
        query = "SELECT id FROM `cloud_assignments`.`user` WHERE username = '%s' AND password = '%s'" % (uname, pwd)
        print(query)
        cur.execute(query)
        result_set = cur.fetchall()
        for row in result_set:
            app.config['USER_ID'] = row[0]
        return jsonify(results=data)
    except Exception as e:
        print("Exception at line number: {}".format(sys.exc_info()[-1].tb_lineno))
        print e
        data = { "login" : False }
        return jsonify(results=data)

@app.route('/upload_file_db', methods=['GET', 'POST'])
def UploadDB():
    try:
        if request.method == 'POST':
            print("0th If")
            local_file = request.files['generic_file']
            # local_file.save(os.path.join(app.config['TEMP_FOLDER'], 'temp_file'))
            # size = os.path.getsize(os.path.join(app.config['TEMP_FOLDER'], 'temp_file'))
            # os.remove(os.path.join(app.config['TEMP_FOLDER'], 'temp_file'))
            # if hasMaxSize(size) == "True":
            #     print("1st if")
            #     return app.send_static_file('file_size_limit.html')
            # if reachedLimit(size) == "True":
            #     print("2nd if")
            #     return app.send_static_file('total_size_limit.html')
            # if local_file and valid_file_ext(local_file.filename):
            filename = secure_filename(local_file.filename)
            unix_time = str(time.time())
            local_file_name = unix_time.split('.')[0] + '_'+ filename
            file_desc = request.form['generic_desc']
            local_file.save(os.path.join(app.config['UPLOAD_FOLDER'], local_file_name))
            print("3rd if")
                # with open(os.path.join(app.config['UPLOAD_FOLDER'], local_file_name), 'rb') as f:
                #     content = f.read()
                #     InsertUserFile(filename, file_desc, local_file_name, str(unicode(content)))
        return app.send_static_file('index.html')            
    except Exception as e:
        print("Exception at line number: {}".format(sys.exc_info()[-1].tb_lineno))
        print e
        return app.send_static_file('index.html')

def InsertUserFile(file_name, file_desc, local_file_name, file_data):
    try:
        user_id = app.config['USER_ID']
        print(app.config['USER_ID'])
        conn = pymysql.connect(**connection_properties)
        cur = conn.cursor()
        cur.execute("INSERT INTO `cloud_assignments`.`file_uploads_metadata`(file_name, file_desc, local_file_name, file_data, user_id) VALUES(" +
                                "  '%s'," % file_name +
                                "  '%s'," % file_desc +
                                "  '%s'," % local_file_name +
                                "  %s," % file_data +
                                "  {}".format(user_id) +
                                ")")
        cur.close()
        conn.close()
    except Exception as e:
        print("Exception at line number: {}".format(sys.exc_info()[-1].tb_lineno))
        print e
        return app.send_static_file('error.html')

@app.route('/download/<fileid>')
def Download(fileid):
    try:
        conn = pymysql.connect(**connection_properties)
        cur = conn.cursor()
        cur.execute("SELECT file_name, file FROM `cloud_assignments`.`file_uploads_metadata` WHERE file_id = %s" % fileid)
        result_set = cur.fetchone()
        for row in result_set:
            filename = row["file_name"]
            file = row["file"]
            request.send_response(200)
            request.send_header('Content-Type', 'application/octet-stream')
            request.send_header('Content-Disposition', 'attachment;','filename=%s' % filename)
            return file
    except Exception as e:
        print("Exception at line number: {}".format(sys.exc_info()[-1].tb_lineno))
        print e
        #return redirect('/')

@app.route('/getPassword/<user>')
def GetPassword(user):
    try:
        conn = pymysql.connect(**connection_properties)
        cur = conn.cursor()
        cur.execute("SELECT password FROM `cloud_assignments`.`user` WHERE username = '%s'" % user)
        result_set = cur.fetchone()
        for row in result_set:
            data = { "password": row }  
            return jsonify(results=data)
    except Exception as e:
        print("Exception at line number: {}".format(sys.exc_info()[-1].tb_lineno))
        print e
        #return redirect('/')

def read_file(filename):
    try:
        with open(filename, 'rb') as f:
            file = f.read()
        return file
    except Exception as e:
        print("Exception at line number: {}".format(sys.exc_info()[-1].tb_lineno))
        print e
        #return redirect('/')

@app.route('/files')
def GetFiles():
    try:
        f = []
        sizes = []
        total = 0
        print(app.config['UPLOAD_FOLDER'])
        for (dirpath, dirnames, filenames) in walk(app.config['UPLOAD_FOLDER']):
            f.extend(filenames)
            break
        for i in range(len(f)):
            size = os.path.getsize(os.path.join(app.config['UPLOAD_FOLDER'], f[i]))
            total += size
            sizes.append(size)
        data = {
            "files" : f,
            "sizes" : sizes,
            "total" : total
        }
        return jsonify(results=data)
        # conn = pymysql.connect(**connection_properties)
        # cur = conn.cursor()
        # cur.execute("SELECT file_name, file_id FROM `cloud_assignments`.`file_uploads_metadata` WHERE status = 1")
        # result_set = cur.fetchall()
        # for row in result_set:
        #     f.append(row["file_name"])
        #     f_ids.append(row["file_id"])
        # cur.close()
        # conn.close()
        # data = { 
        #     "files": f,
        #     "ids": f_ids
        # }
        # return jsonify(results=data)
    except Exception as e:
        print("Exception at line number: {}".format(sys.exc_info()[-1].tb_lineno))
        print e
        #return redirect('/')

@app.route('/delete/<file_id>')
def DeleteFiles(file_id):
    try:
        conn = pymysql.connect(**connection_properties)
        cur = conn.cursor()
        cur.execute("UPDATE `cloud_assignments`.`file_uploads_metadata` SET status = 1 WHERE file_id = %s" % file_id)
        result_set = cur.fetchall()
        for row in result_set:
            f.append(row["file_name"])
            f_ids.append(row["file_id"])

        cur.execute("SELECT file_name FROM `cloud_assignments`.`file_uploads_metadata` WHERE file_id = %s" % file_id)
        result_set = cur.fetchone()
        for row in result_set:
            os.remove(os.path.join(app.config['UPLOAD_FOLDER'], row["file_name"]))
        #return redirect('/')
    except Exception as e:
        print("Exception at line number: {}".format(sys.exc_info()[-1].tb_lineno))
        print e
        #return redirect('/')

def reachedLimit(filesize):
    limit = 1024 # 10 MB
    folder_size = os.path.getsize(os.path.join(app.config['UPLOAD_FOLDER']))
    if (folder_size + filesize) > limit:
        return "True"
    else:
        return "False"

def hasMaxSize(filesize):
    limit = 1024 # 1 MB
    if filesize > limit:
        return "True"
    else:
        return "False"

port = os.getenv('PORT', '8000')
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(port))