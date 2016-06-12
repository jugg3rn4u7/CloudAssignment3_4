#!/bin/bash

echo "Creating subfolder to store data - ./day/$DAY"
mkdir ./data/$DAY
cd ./data/$DAY

wget -r $1
