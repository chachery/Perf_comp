#!/usr/bin/python
from .logAndPrint import warning_writer

def checkThreshold(logf, value):
  try:
    value = float(value)
    if value < 0:
      warning_writer(logf, "invalid input of '-s', it will be set in default('0')!")
    elif value >1:
      warning_writer(logf, "invalid input of '-s', it will be set in at 1!")
  except ValueError:
    warning_writer(logf, "invalid input of '-s', it will be set in default('0')!")
