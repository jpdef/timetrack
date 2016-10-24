#!/usr/bin/env python2.7
import pyunix
import sys
import os
import subprocess
import csv
import time
import datetime
import encryptsc
import argparse

class tracker:    
    def __init__(self):
        self.data_dir = os.environ.get("TIMETRACKPATH")
        self.month_file = self.data_dir + "/october.csv"
        self.month_file_scramble = self.data_dir + "/october.csv.asc"
        self.todayCommit = datetime.date.today().strftime("%d-%m-%y")

        self.db = []
        with open(self.month_file,"rb") as trackfile:
            reader = csv.DictReader(trackfile)
            for row in reader:
                self.db.append(row)
    
    def print_day(self,dates):
        datelist = self.getDates(dates)
        total = 0 
        for item in datelist:
            itemtime = self.calcTimeRow(item)
            print "{} : {} minutes : {} : {}".format(item['date'],itemtime,item['subject'],item['description'] )
            total += itemtime
        print "Total := {} minutes".format(total)
     
    def print_week(self,dates):
        pass
   
 
    def how_many_minutes(self,start,end):
        hstart , mstart = start.tm_hour, start.tm_min
        hend   , mend = end.tm_hour, end.tm_min
        
        return (hend - hstart)*60 + (mend -mstart)

    def write_start(self,subject):
        with open(month_file,"a") as trackfile:
            trackwriter = csv.writer(trackfile, delimiter=',')
            trackwriter.writerow([subject,datetime.datetime.now().strftime("%H:%M")])
    
    def write_date(self):
        with open(self.month_file,"a") as trackfile:
            trackwriter = csv.writer(trackfile, delimiter=',')
            trackwriter.writerow([datetime.datetime.now().strftime("%m-%d")])

    def calcTimeRow(self,d):
        start = time.strptime(d['start'], "%H:%M")
        end   = time.strptime(d['end'], "%H:%M")
        return  self.how_many_minutes(start,end)

    def getDates(self,dates):
        datelist = []
        for date in dates:
            datelist += self.getDate(date)
        datelist = filter(lambda x : x['subject'] in self.tickets, datelist ) 
        return datelist 

    def getDate(self,strdate):
        time = []
        for d in self.db:
            if (d['date'] == strdate):
                time.append(d) 
        return time

    def update_remote(self,forWhom):
        whom = [w for w in forWhom]
        encryptsc.encrypt(whom,self.month_file)
        encryptsc.gitcommit(self.todayCommit)
        encryptsc.gitpush()
    
    def update_local(self):
      encryptsc.gitpull()
      encryptsc.decrypt(self.month_file_scramble)
    
    def addFn(self,content):
      with open(self.month_file,"a") as trackfile:
          trackwriter = csv.writer(trackfile, delimiter=',')
          now  = datetime.datetime.now().strftime("%D")
          content.insert(0,now)
          trackwriter.writerow(content)
