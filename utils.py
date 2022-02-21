import sys

VERBOSITY = 1

def set_verbosity(verbosity : int):
    global VERBOSITY
    VERBOSITY = verbosity

def verbose_print(value:str, sep=' ', end='\n', file=sys.stdout, flush=False):
    if VERBOSITY > 0:
        print(value, sep=sep, end=end, file=file, flush=flush)

def vverbose_print(value:str, sep=' ', end='\n', file=sys.stdout, flush=False):
    if VERBOSITY > 1:
        print(value, sep=sep, end=end, file=file, flush=flush)