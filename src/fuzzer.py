#!/usr/bin/python3

import sys

from mutators.csv import CSVFuzz
from mutators.json import JSONFuzz

if len(sys.arv) != 3:
    print("Usage: ./fuzzer program sampleinput.txt")
    sys.exit()


try:
    inputFile = open(sys.argv[2], 'r')
    inputStr = inputFile.read().strip()


except OSError:
    print(f"Couldn't open input file: {sys.argv[2]}")
    sys.exit()

fuzz = None
if JSONFuzz(inputStr).isType():
    fuzz = JSONFuzz(inputStr)
elif CSVFuzz(inputStr).isType():
    fuzz = CSVFuzz(inputStr)
else:
    print(f"Couldn't parse input file")
    sys.exit()
    

# fuzz.fuzz() ?

