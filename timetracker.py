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
import rt
import requests
#import browsercookie

class tracker:    
    def __init__(self):
        self.data_dir = os.environ.get("TIMETRACKPATH")
        self.month_file = self.data_dir + "/febuary.csv"
        self.month_file_scramble = self.data_dir + "/febuary.csv.asc"
        self.todayCommit = datetime.date.today().strftime("%d-%m-%y")

        self.db = []
        with open(self.month_file,"rb") as trackfile:
            reader = csv.DictReader(trackfile)
            for row in reader:
                self.db.append(row)
  
    """
     Request Tracker Functions 

       -lists tickets that are owned by user
       -submits time and message to tickets 
    """


    def list_tickets(self):
        rt.listTickets(self.data_dir)
   
    

    def submit_report(self,dates):
        #Needs to write seperate report for each ticket in list
        #Search through tickets find ticket numbers
	if "all" in self.tickets:
	   self.tickets = list(set(self.getTicketNoFromDates(dates)))
        
        for t in self.tickets:
            print "Ticket:", t
            #Collect time for tickets
            totalTime = self.getTimeOnTicket(dates,t)
            #Generate report
            report = self.getReportonTicket(dates,t)
            #Post
            print "Here is your report:"
	    print report, totalTime, '\n'
	    toContinue = raw_input("Does this look correct? [y/n]\n")
	    if toContinue is  "y":
                rt.submitToTicket(self.data_dir,report,totalTime,t  )
   
    """
    Gets all ticket numbers which have dates specified by user arguement
    or function argument
    """
    def getTicketNoFromDates(self,dates=None):
        if dates is None:
	   dates = self.dates
        rows = self.getDates(dates)
        ticket_numbers = [x['ticketnumber'] for x in rows]
        return ticket_numbers
    

    """
    Write code here to test out
    """
    def tester(self,dates=None):
	print "foo"


    """
    Prints a report with each row that has date specified by function
    Also prints a sum of time for these rows
    """
    def print_dates(self,dates):
        datelist = self.getDates(dates)
        total = 0
        for item in datelist:
            itemtime = self.calcTimeRow(item)
            print "{} : {} minutes : {} : {}".format(item['date']
                    ,itemtime,item['ticketnumber'],item['description'] )
            total += itemtime
        print "Total := {} minutes".format(total)
    
    """
    Calculates the time for all rows that have ticket number and date
    specified by function
    """
    def getTimeOnTicket(self, dates,ticket):
        datelist = self.getDates(dates,ticket)
        total = 0
        for item in datelist:
            itemtime = self.calcTimeRow(item)
            total += itemtime       
        return total


    
    def getReportonTicket(self, dates,ticket): 
        datelist = self.getDates(dates,ticket)
        itemreport = ""
        
        for item in datelist:
            itemtime = self.calcTimeRow(item)
            itemreport += "{} : {} minutes : {} : {}\n".format(item['date'],itemtime,item['ticketnumber'],item['description'] )
        return itemreport 

 
    def how_many_minutes(self,start,end):
        hstart , mstart = start.tm_hour, start.tm_min
        hend   , mend = end.tm_hour, end.tm_min
        
        return (hend - hstart)*60 + (mend -mstart)

    def write_start(self,ticketnumber):
        with open(month_file,"a") as trackfile:
            trackwriter = csv.writer(trackfile, delimiter=',')
            trackwriter.writerow([ticketnumber,datetime.datetime.now().strftime("%H:%M")])
    
    def write_date(self):
        """
        Creates trackwriter
        Wirtes the current date into csv file
        """
        with open(self.month_file,"a") as trackfile:
            trackwriter = csv.writer(trackfile, delimiter=',')
            trackwriter.writerow([datetime.datetime.now().strftime("%m-%d")])

    def calcTimeRow(self,d):
        start = time.strptime(d['start'], "%H:%M")
        end   = time.strptime(d['end'], "%H:%M")
        return  self.how_many_minutes(start,end)

    """
    Returns list of tickets from specified dates,
    and if tickets are specifcied then also ticketnumber
    """
    def getDates(self,dates,ticket=None):
        datelist = []
        for date in dates:
            datelist += self.getDate(date)
        if ticket is None and self.tickets:
            if 'all' not in self.tickets:
               datelist = filter(lambda x : x['ticketnumber'] in self.tickets, datelist ) 
        elif ticket:
            if 'all' not in ticket:
               datelist = filter(lambda x : x['ticketnumber'] in ticket, datelist )

        return datelist 

    def getDate(self,strdate):
        time = []
        for d in self.db:
            if (d['date'] == strdate):
                time.append(d) 
        return time

    """
    Github functions to update code with encrypted file
    """
    def update_remote(self,forWhom):
        whom = [w for w in forWhom]
        encryptsc.encrypt(whom,self.month_file)
        encryptsc.gitcommit(self.todayCommit,self.data_dir)
        encryptsc.gitpush(self.data_dir)
    
    def update_local(self):
      encryptsc.gitpull(self.data_dir)
      encryptsc.decrypt(self.month_file_scramble,self.month_file)
    
    def addFn(self,content):
      with open(self.month_file,"a") as trackfile:
          trackwriter = csv.writer(trackfile, delimiter=',')
          now  = datetime.datetime.now().strftime("%D")
          content.insert(0,now)
          trackwriter.writerow(content)
