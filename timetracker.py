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
# import browsercookie

INDIRECT_TIME = 60  # 1 hours break per day


class tracker:

    def __init__(self):
        self.ttpath = os.environ.get("TIMETRACKPATH")
        self.month_file = os.path.join(self.ttpath,"data/march.csv")
        self.month_file_scramble = os.path.join(self.ttpath,"data/march.csv.asc")
        self.todayCommit = datetime.date.today().strftime("%d-%m-%y")

        self.db = []
        self.rt = rt.RT()
        with open(self.month_file, "rb") as trackfile:
            reader = csv.DictReader(trackfile)
            for row in reader:
                self.db.append(row)

    """
     RT FN's
    """

    """
    list_tickets()
       lists tickets that are owned by user
    """

    def list_tickets(self):
        self.rt.listTickets(self.ttpath)

    """
     submit_report()
       -submits time and message to RT 
    """
    def submit_report(self,dates):
        # Needs to write seperate report for each ticket in list
        # Search through tickets find ticket numbers
        if "all" in self.tickets:
            self.tickets = list(set(self.get_ticket_numbers_from_dates(dates)))
        totalTime = 0.0
        print self.tickets
        for t in self.tickets:
            totalTime  += self.get_time_from_ticket(dates,t)

        indirect_time =  len(dates)*INDIRECT_TIME        
        
        print "This is the total time worked", totalTime
        for t in self.tickets:
            print "Ticket:", t
            # Collect time for tickets
            time = self.get_time_from_ticket(dates,t)
            
            # Calculate Indirect Time
            if self.indirect:
                itt = round(indirect_time * time/totalTime)
                time += itt
    
            # Generate report
            report = self.get_report_from_ticket(dates,t)
            
            if self.indirect:
                report += "+ indirect " + str(itt)  +  "\n"

            # Post
            print "Here is your report:"
            print report, time, '\n'
            toContinue = raw_input("Does this look correct? [y/n]\n")
            if toContinue is  "y":
                self.rt.submitToTicket(self.ttpath,report,time,t  )
   
    """
    HELPER FN's
    """


    """
    get_tickets_from_dates
        Gets all ticket numbers which have dates specified by user arguement
         or function argument
         @param dates
    """
    def get_ticket_numbers_from_dates(self,dates=None):
        if dates is None:
            dates = self.dates
        rows = self.get_tickets_from_dates(dates)
        ticket_numbers = [x['ticketnumber'] for x in rows]
        return ticket_numbers
    

    """
    test_it()
       Write code here to test out
       @param dates 
    """
    def test_it(self,dates=None):
        print "foo"

    """
    add_row
        add a row to csv file
        @param content 
    """
    def add_row(self,content):
      with open(self.month_file,"a") as trackfile:
          trackwriter = csv.writer(trackfile, delimiter=',')
          now  = datetime.datetime.now().strftime("%D")
          content.insert(0,now)
          trackwriter.writerow(content)


    """
    print_dates
    Prints a report with each row that has date specified by function
    Also prints a sum of time for these rows
    @param dates
    """
    def print_dates(self,dates):
        datelist = self.get_tickets_from_dates(dates)
        total = 0
        for item in datelist:
            itemtime = self.get_time_from_row(item)
            print "{} : {} minutes : {} : {}".format(item['date']
                    ,itemtime,item['ticketnumber'],item['description'] )
            total += itemtime
        print "Total := {} minutes".format(total)
    
    """
    get_time_from_ticket()
    Calculates the time for all rows that have ticket number and date
    specified by function
    @param dates
    @param tickets
    """
    def get_time_from_ticket(self, dates,ticket):
        datelist = self.get_tickets_from_dates(dates,ticket)
        total = 0
        for item in datelist:
            itemtime = self.get_time_from_row(item)
            total += itemtime       
        return total


    """
    get_report_from_ticket()
        Writes a messeage with time and information for each ticket for each date
        @param dates
        @ticket
    """
    def get_report_from_ticket(self, dates,ticket): 
        datelist = self.get_tickets_from_dates(dates,ticket)
        itemreport = ""
        
        for item in datelist:
            itemtime = self.get_time_from_row(item)
            itemreport += "{} : {} minutes : {} : {}\n".format(item['date'],itemtime,item['ticketnumber'],item['description'] )
        return itemreport 

 
    def get_minutes(self,start,end):
        hstart , mstart = start.tm_hour, start.tm_min
        hend   , mend = end.tm_hour, end.tm_min
        
        return (hend - hstart)*60 + (mend -mstart)

    def get_time_from_row(self,d):
        start = time.strptime(d['start'], "%H:%M")
        end   = time.strptime(d['end'], "%H:%M")
        return  self.get_minutes(start,end)

    """
    Returns list of tickets from specified dates,
    and if tickets are specifcied then also ticketnumber
    """
    def get_tickets_from_dates(self,dates,ticket=None):
        datelist = []
        for date in dates:
            datelist += self.get_date(date)
        if ticket is None and self.tickets:
            if 'all' not in self.tickets:
               datelist = filter(lambda x : x['ticketnumber'] in self.tickets, datelist ) 
        elif ticket:
            if 'all' not in ticket:
               datelist = filter(lambda x : x['ticketnumber'] in ticket, datelist )

        return datelist 

    def get_date(self,strdate):
        time = []
        for d in self.db:
            if (d['date'] == strdate):
                time.append(d) 
        return time

    """
    GIT FN's
    """
    def update_remote(self,forWhom):
        whom = [w for w in forWhom]
        encryptsc.encrypt(whom,self.month_file)
        encryptsc.gitcommit(self.todayCommit,self.ttpath)
        encryptsc.gitpush(self.ttpath)
    
    def update_local(self):
      encryptsc.gitpull(self.ttpath)
      encryptsc.decrypt(self.month_file_scramble,self.month_file)
    
