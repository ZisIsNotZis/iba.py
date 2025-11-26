#!/bin/env python
from .iba import *
from sys import argv
from json import load, dump


"""
A basic CLI that converts between .json and .dat
"""
if __name__ == '__main__':
    if argv[1:] and argv[1].endswith('.json'):
        enc(argv[1] + '.dat', *load(open(argv[1], 'r')))
    elif argv[1:] and argv[1].endswith('.dat'):
        dump(dec(argv[1]), open(argv[1] + '.json', 'w'), default=str)
    else:
        print('usage:')
        print(argv[0], '*.dat => *.json')
        print(argv[0], '*.json => *.iba')
