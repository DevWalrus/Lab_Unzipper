import re
import sys
from typing import List

VERBOSITY = 0

def set_verbosity(verbosity : int):
    global VERBOSITY
    VERBOSITY = verbosity

def verbose_print(value:str, sep=' ', end='\n', file=sys.stdout, flush=False):
    if VERBOSITY > 0:
        print(value, sep=sep, end=end, file=file, flush=flush)

def vverbose_print(value:str, sep=' ', end='\n', file=sys.stdout, flush=False):
    if VERBOSITY > 1:
        print(value, sep=sep, end=end, file=file, flush=flush)

def read_file(f_name:str) -> List[str]:
    with open(f_name) as fp:
        lines = fp.readlines()
    for i in range(len(lines)):
        lines[i] = lines[i].strip()
        if lines[i].startswith("//"):
            lines[i] = ''
    return lines

def find_tests(f_name:str) -> List[str]:
    lines = read_file(f_name)
    tests_to_find = lines.count('@Test')
    test_found = 0
    test_names = []
    while tests_to_find > 0:
        attr = lines.index('@Test', test_found)
        test_found = attr + 1
        test_names.append(re.split('[ \t]+', lines[test_found])[2][:-2])
        tests_to_find -= 1
    return test_names