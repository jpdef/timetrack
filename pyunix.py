#!/usr/bin/env python2.7
import subprocess
import string
import os
import time
import datetime


#Global Vars
today = datetime.date.today().strftime("%d-%m-%y")

startup_targets =["<name>","<facility>","<uname>",
                   "<date>","<arch>","<bin>","<iocname>"]

startup_subs =["Jacob DeFilippis","Motion Controls","jpdef",
                   today,"linux-x86","bar","foo"]
startupdir="sioc-example"
startupname="startup.cmd"


def docmd(cmd,uargs,input=None):
  cmd += " "
  cmd += " ".join(uargs)
  p = subprocess.Popen(cmd, 
      stdout=subprocess.PIPE,
      stdin=subprocess.PIPE,
      shell=True,
      executable='/bin/zsh'
      )
  if(input is None):
    return p.stdout.read()
  else:
      p.stdin.write(input)
      p.stdin.close()
      return p.stdout.read()

def echo(sound):
    return docmd("echo",[sound])

def cd(directory):
    return docmd("cd",[directory])

def jump(path,cmd,uargs):
  cwd = os.getcwd()
  jmpcmd = " ".join(["cd",path,"&&",cmd,"&&","cd",cwd])
  return docmd(jmpcmd,[])

def pwd():
  return docmd("pwd",[])

def mkdir(fname,fpath=os.getcwd()):
    strdir = os.path.join(fpath,fname)
    return docmd("mkdir",[strdir])

def mklink(target,link):
    return docmd("ln",["-s",target,link])

def cat(fname,fpath=os.getcwd()):
    strdir = os.path.join(fpath,fname)
    return docmd("cat",[strdir])

def sed(input,target,sub):
    sedargs=[]
    for r in zip(target,sub):
        sedargs.append("-e")
        sedargs.append('/'.join(["s",r[0],r[1],"g"]))
    return docmd("sed",sedargs,input)

def mkstartup():
    template = cat("startup.template")
    startupstr = sed(template,startup_targets,startup_subs)
    with open(os.path.join(startupdir,startupname),'a') as fstartup:
        fstartup.write(startupstr)

def pjoin(p1,p2):
  return os.path.join(p1,p2)

def mkiocdirtest():
   mkdir("sioc-example")
   mkstartup()
   mklink(pjoin(startupdir,startupname),"sioc-example/st.cmd")
   mklink("bar","sioc-example/iocSpecificRelease")
