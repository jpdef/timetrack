#!/usr/bin/env python2.7
import pyunix
import subprocess
import string
import os
import time
import datetime


def encrypt(users,fname):
  cmd = "gpg";
  uargs = ['-r ' + user for user in users ]
  uargs+=["--armor","--encrypt",fname]
  return pyunix.docmd(cmd,uargs)

def decrypt(fname,target):
  cmd = "gpg"
  uargs=["--output",target,"--decrypt",fname]
  return pyunix.docmd(cmd,uargs)

def gitdiff(path="."):
  cmd = "git"
  uargs=["--git-dir",os.path.join(path,".git"),"--no-pager","diff","master","origin/master"]
  return pyunix.docmd(cmd,uargs) 

def gitpush(path="."):
  cmd = "git"
  uargs=["--git-dir",os.path.join(path,".git"),"push","origin","master"]
  return pyunix.docmd(cmd,uargs) 

def gitpull(path="."):
  cmd = "git"
  uargs=["--git-dir",os.path.join(path,".git"),"pull","origin","master"]
  return pyunix.docmd(cmd,uargs)

def gitcommit(comment,path="."):
  cmd = "git"
  uargs=["--git-dir",os.path.join(path,".git"),"commit","-a","-m",comment]
  return pyunix.docmd(cmd,uargs)

