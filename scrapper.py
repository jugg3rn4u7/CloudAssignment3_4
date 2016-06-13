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
from flask import Flask
from werkzeug import secure_filename
import subprocess

BASEPATH = os.path.dirname(os.path.abspath(__file__))

DOWNLOADER = os.path.join( BASEPATH, 'download_data.sh' ) 
OUTPUT = os.path.join( BASEPATH, 'output.txt' )
URL = ["https://inventory.data.gov/dataset/032e19b4-5a90-41dc-83ff-6e4cd234f565/resource/38625c3d-5388-4c16-a30f-d105432553a4/download/postscndryunivsrvy2013dirinfo.csv"]

try:
	startTime = int(round(time.time() * 1000))
	for i in range(len(URL)):
		os.system("time %s" % DOWNLOADER + " %s" % URL[i])   
	endTime = int(round(time.time() * 1000))
	print("Time taken to download file : ", endTime - startTime,'ms') 
except Exception as e:
    print("Exception at line number: {}".format(sys.exc_info()[-1].tb_lineno))
    print("Exception : %s" % e)
