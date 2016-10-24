#!/usr/bin/env python2.7
import pyunix
import subprocess
import string
import os
import time
import datetime


def encrypt(users,fname):
  cmd = "gpg";
  uargs = []
  for user in users:
      uargs += ['-r',user]
  uargs+=["--armor","--encrypt",fname]
  print uargs
  return pyunix.docmd(cmd,uargs)

def decrypt(fname):
  cmd = "gpg"
  uargs=["--decrypt",fname]
  return pyunix.docmd(cmd,uargs)

def gitdiff():
  cmd = "git"
  uargs=["--no-pager","diff","master","origin/master"]
  return pyunix.docmd(cmd,uargs) 

def gitpush():
  cmd = "git"
  uargs=["push","origin","master"]
  return pyunix.docmd(cmd,uargs) 

def gitpull():
  cmd = "git"
  uargs=["pull","origin","master"]
  return pyunix.docmd(cmd,uargs)

def gitcommit(comment):
  cmd = "git"
  uargs=["commit","-a","-m",comment]
  return pyunix.docmd(cmd,uargs)

