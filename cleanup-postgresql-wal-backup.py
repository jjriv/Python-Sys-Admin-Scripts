#!/usr/bin/python

import os
import time
import datetime

path = '/postgresql_wal_backup'
hoursback = 36;
timebackdt = datetime.datetime.now() - datetime.timedelta(hours=hoursback)

files = sorted(os.listdir(path))
for file in files:
    ctimedt = datetime.datetime.fromtimestamp(os.stat(path + '/' + file).st_ctime)
    if ctimedt < timebackdt:
        os.remove(path + '/' + file)
