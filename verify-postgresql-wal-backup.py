#!/usr/bin/python

#verify postgresql wal backup.
#1) notify if old files still laying around
#2) notify if files not showing up or missing

import os
import time
import datetime
import smtplib
import socket

path = '/postgresql_wal_backup'
hoursback = 48;
hoursrecent = 12;
timebackdt = datetime.datetime.now() - datetime.timedelta(hours=hoursback)
timerecentdt = datetime.datetime.now() - datetime.timedelta(hours=hoursrecent)
hostname = socket.gethostname().split('.')[0]

files = sorted(os.listdir(path))
oldfiles = []
recentfiles = []
for file in files:
    ctimedt = datetime.datetime.fromtimestamp(os.stat(path + '/' + file).st_ctime)
    filestats = str(ctimedt) + ' | ' + file
    if ctimedt < timebackdt:
        oldfiles.append(str(timebackdt) + ' | ' + filestats)
    elif ctimedt > timerecentdt:
        recentfiles.append(str(timerecentdt) + ' | ' + filestats)

#mail headers
msg =       "From: backup@pelagodesign.com\r\n"
msg = msg + "To: backup@pelagodesign.com\r\n"
msg = msg + "Subject: PostgreSQL WAL Backup Issue on " + hostname + "\r\n"
msg = msg + "\r\n"

#if we found any old files, email a message
sendmail = False
if len(oldfiles) > 0:
    msg = msg + "There are old WAL files older than " + str(hoursback) + " hours ago in the backup that should not be there.\n"
    msg = msg + "\n".join(oldfiles)
    sendmail = True
elif len(recentfiles) == 0:
    msg = msg + "Recent WAL files from the last " + str(hoursrecent) + " hours are missing.\n"
    sendmail = True

if sendmail == True:
    if hostname == 'd1fr':
        mailserver = smtplib.SMTP('192.168.132.78')
    else:
        mailserver = smtplib.SMTP('10.186.33.143')
    mailserver.sendmail("backup@pelagodesign.com", "backup@pelagodesign.com", msg)
