#!/usr/bin/python
import sys

log = 'log'

#red
def error_msg(msg):
    msg = "\033[31m" + msg + "\033[0m"
    return msg

def error_writer(msg):
    msg = 'Error: ' + msg
    log_w(msg + '\n')
    sys.exit(error_msg(msg))

#yellow
def warning_msg(msg):
    msg = "\033[33m" + msg + "\033[0m"
    return msg

def warning_writer(msg):
    msg = 'Warning: ' + msg
    log_w(msg + '\n')
    print(warning_msg(msg))

#Produce a log file
def log_w(msg):
    with open(log,'a+') as lf:
        lf.write(msg)

def log_writer(msg):
    log_w(msg + '\n')
    print(msg)
