import os
from pyunix import docmd
from HTMLParser import HTMLParser
from collections import OrderedDict

#no escape
#magicstring = "\"UpdateContent=\"{}\"&UpdateTimeWorked=\"{}\"&UpdateTimeWorked-Units=\"minutes\"&SubmitTicket=\"Update Ticket\"&UpdateType=response&Action=\"Respond\"&UpdateAttach=1\"  \"https://rt.cosylab.com/rt3/Ticket/Update.html?id={}\" "

magicstring = "\"UpdateContent={}&UpdateTimeWorked={}&UpdateTimeWorked-Units=minutes&SubmitTicket=Update Ticket&UpdateType=response&Action=Respond&UpdateAttach=1\"  \"https://rt.cosylab.com/rt3/Ticket/Update.html?id={}\" "

magicstring2 = "https://rt.cosylab.com/rt3/Search/Results.html\?Query\=%20Owner%20%3D%20%27394269%27%20AND%20%20\(%20%20Status%20%3D%20%27new%27%20OR%20Status%20%3D%20%27open%27%20\)"

class bcolors:
      red = "\033[95m"
      end = "\033[0m"

class RTHTMLPARSER(HTMLParser):
    isLink = False
    isTableRow  = False
    extractedData = {}
    ticketnumbers=[]
    ticketnames = []

    def handle_starttag(self,tag,attrs):
	if tag == 'a' :
           if len(attrs[0]) > 1 and 'id=' in attrs[0][1]:
              self.isLink = True

    def handle_endtag(self,tag):
        if tag == 'a' and self.isLink :
           self.isLink = False
           

    def handle_data(self,data):
        if self.isLink:
           if data.isdigit():
               self.ticketnumbers.append(int(data))
           else:
               self.ticketnames.append(data)

    def getData(self):
         self.extractedData = OrderedDict(zip(self.ticketnumbers,self.ticketnames))
         if self.extractedData is None:
             print "No data parse first"
             return {}
         else:
             return self.extractedData


parser = RTHTMLPARSER()


def submitToTicket(datadir,msg,time,ticketnumber):
    args = ["--load-cookies",os.path.join(datadir,"cookies.txt"),"--post-data"]
    url = magicstring.format(msg,time,ticketnumber)
    args.append(url)
    docmd("wget",args)

def listTickets(datadir):
    args = ["--load-cookies",os.path.join(datadir, "cookies.txt"),"-S","-O","-"]
    args.append(magicstring2)
    htmldata =  docmd("wget",args)
    extractedData =  parseTicketHTML(htmldata)
    ticketPrint(extractedData)

def ticketPrint(ticketData):
    temp = 0
    for k in ticketData:
        l = k >> 9
	if l == temp:
	   print '\t',k, ticketData[k]
        else:
	   print bcolors.red, k, ticketData[k],bcolors.end
	temp = l 

def parseTicketHTML(htmldata):
    #need a more robust way of parsing escape charaters
    htmldata =  htmldata.replace("&#38;","and")
    htmldata =  htmldata.replace("&#39;","'")
    parser.feed(htmldata)
    return parser.getData()
    
