#!/bin/sh

echo 'Fetching git files'
wget https://raw.githubusercontent.com/ithomps4/pSSID/master/api.py
wget https://raw.githubusercontent.com/ithomps4/pSSID/master/pSSID_skeleton.json
wget https://raw.githubusercontent.com/ithomps4/pSSID/master/parse.py
wget https://raw.githubusercontent.com/ithomps4/pSSID/master/psjson.py

echo 'Configuring logger'
wget https://raw.githubusercontent.com/ithomps4/pSSID/master/conf/pSSID-logger.conf
sudo mv pSSID-logger.conf /etc/rsyslog.d/pSSID-logger.conf
sudo service rsyslog restart
