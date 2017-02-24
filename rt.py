import os
import requests
import secrets

from pyunix import docmd
from HTMLParser import HTMLParser
from collections import OrderedDict
#no escape
#magicstring = "\"UpdateContent=\"{}\"&UpdateTimeWorked=\"{}\"&UpdateTimeWorked-Units=\"minutes\"&SubmitTicket=\"Update Ticket\"&UpdateType=response&Action=\"Respond\"&UpdateAttach=1\"  \"https://rt.cosylab.com/rt3/Ticket/Update.html?id={}\" "

magicstring = "\"UpdateContent={}&UpdateTimeWorked={}&UpdateTimeWorked-Units=minutes&SubmitTicket=Update Ticket&UpdateType=response&Action=Respond&UpdateAttach=1\"  \"https://rt.cosylab.com/rt3/Ticket/Update.html?id={}\" "

magicstring2 = "https://rt.cosylab.com/rt3/Search/Results.html\?Query\=%20Owner%20%3D%20%27394269%27%20AND%20%20\(%20%20Status%20%3D%20%27new%27%20OR%20Status%20%3D%20%27open%27%20\)"

magicstring3 = "https://rt.cosylab.com/rt3/Search/Results.html?Order=DESC%7CASC%7CASC%7CASC&Query=%20Owner%20%3D%20%27394269%27%20AND%20%20(%20%20Status%20%3D%20%27new%27%20OR%20Status%20%3D%20%27open%27%20)&OrderBy=Priority%7C%7C%7C&RowsPerPage=50&Format=%27%3Ca%20href%3D%22%2Frt3%2FTicket%2FDisplay.html%3Fid%3D__id__%22%3E__id__%3C%2Fa%3E%2FTITLE%3A%23%27%2C%0D%0A%27%3Ca%20href%3D%22%2Frt3%2FTicket%2FDisplay.html%3Fid%3D__id__%22%3E__Subject__%3C%2Fa%3E%2FTITLE%3ASubject%27%2C%0D%0A%27__Priority__%2FTITLE%3APriority%27%2C%0D%0A%27__QueueName__%27%2C%0D%0A%27__ExtendedStatus__%27%2C%0D%0A%27%3Ca%3ETake%3C%2Fa%3E%2FTITLE%3A%26nbsp%3B%20%27"
class bcolors:
      red     = '\033[95m'
      OKBLUE  = '\033[94m'
      OKGREEN = '\033[92m'
      WARNING = '\033[93m'
      FAIL    = '\033[91m'
      end = "\033[0m"
      colors = ['\033[95m','\033[94m','\033[92m','\033[93m','\033[91m']

class RTHTMLPARSER(HTMLParser):
    isLink = False
    isTableRow  = False
    tdcount = 0
    extractedData = {}
    ticketnumbers=[]
    ticketnames = []
    queuenames = []
  
    #forth TD
    def handle_starttag(self,tag,attrs):
        if tag == 'a' :
            if len(attrs[0]) > 1 and 'id=' in attrs[0][1] :
                self.isLink = True
        
        elif tag == 'tr':
            if len(attrs[0]) > 1:
                if 'evenline' in attrs[0][1]:
                  self.isTableRow = True
                if 'oddline' in attrs[0][1]:
                  self.isTableRow = True
        
        elif tag == 'td':
            if self.isTableRow:
                self.tdcount += 1

    def handle_endtag(self,tag):
        if tag == 'a' and self.isLink :
           self.isLink = False

        if tag == 'tr' and self.isTableRow:
           self.isTableRow = False
           self.tdcount = 0
           

    def handle_data(self,data):
        if self.isLink:
           if data.isdigit():
               self.ticketnumbers.append(int(data))
           else:
               self.ticketnames.append(data)
        
        if self.isTableRow and self.tdcount == 4:
               self.queuenames.append(data)

    def getData(self):
         self.extractedData = zip(self.ticketnumbers,self.ticketnames,self.queuenames)
         if self.extractedData is None:
             print "No data parse first"
             return {}
         else:
             return self.extractedData



class RT():
    def __init__(self):
        self.sess = requests.Session()
        self.parser = RTHTMLPARSER()
        self.login()


    def login(self):
        self.sess.post("https://rt.cosylab.com/rt3/login/login.cgi", data=secrets.secrets,allow_redirects=True)
    
    
    def submitToTicket(self,datadir,msg,time,ticketnumber):
        args = ["--load-cookies",os.path.join(datadir,"cookies.txt"),"--post-data"]
        url = magicstring.format(msg,time,ticketnumber)
        args.append(url)
        docmd("wget",args)
    
    def listTickets(self,datadir):
        """
        args = ["--load-cookies",os.path.join(datadir, "cookies.txt"),"-S","-O","-"]
        args.append(magicstring2)
        htmldata =  docmd("wget",args)
        extractedData =  parseTicketHTML(htmldata)
        ticketPrint(extractedData)
        """
        r = self.sess.get(magicstring3)
        extractedData =  self.parseTicketHTML(r.text)
        self.ticketPrint(extractedData)
    
    def ticketPrint(self,ticketData):
        queues = []
        for e in ticketData:
            queues.append(e[2])
        queues = set(queues)
        for i,q in enumerate(queues):
          for e in ticketData:
            if e[2] == q:
              print bcolors.colors[i % len(bcolors.colors)], e[0], e[1], e[2], bcolors.end

    
    def parseTicketHTML(self,htmldata):
        #need a more robust way of parsing escape charaters
        htmldata =  htmldata.replace("&#38;","and")
        htmldata =  htmldata.replace("&#39;","'")
        self.parser.feed(htmldata)
        return self.parser.getData()
        
