#!/sur/bin/python
class WrongfastaException(Exception):
    def __init__(self, flag):
        self.flag=flag
'''
class NotFoundifError(FileNotFoundError):
    def __init__(self, input_f):
        self.input_f=input_f
'''
