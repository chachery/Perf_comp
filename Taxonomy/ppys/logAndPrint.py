#!/usr/bin/python
import sys

#red
def error_msg(msg):
    msg = "\033[31m" + msg + "\033[0m"
    return msg

def error_writer(logf, msg):
    msg = 'Error: ' + msg
    log_w(logf, msg + '\n')
    sys.exit(error_msg(msg))

#yellow
def warning_msg(msg):
    msg = "\033[33m" + msg + "\033[0m"
    return msg

def warning_writer(logf, msg):
    msg = 'Warning: ' + msg
    log_w(logf, msg + '\n')
    print(warning_msg(msg))

#common
def log_w(logf, msg):
    with open(logf, 'a+') as lf:
        lf.write(msg)

def logAndPrint(logf, msg):
    log_w(logf, msg + '\n')
    print(msg)
