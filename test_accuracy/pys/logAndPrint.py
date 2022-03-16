#!/usr/bin/python

def logAndPrint(logf, message):
    print(message)
    with open(logf, 'a+') as f:
        f.write(message)
