#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Apr  2 09:56:24 2017

Converts files with xlink information into various formats


@author: lukas
"""
import sys
import argparse
import enum






def detect_format(infile_path):
    with open(infile_path, 'r') as f:
        for line in f:
            if line.lstrip().startswith("<xquest"):
                return "xquest"
    return None                
    
    
    
    
    





def main(argv):
    parser = argparse.ArgumentParser()
    parser.add_argument("IN",  type=str, help="Infile to convert")
    args = parser.parse_args(argv[1:])
    
    



if __name__ == '__main__':
    main(sys.argv)