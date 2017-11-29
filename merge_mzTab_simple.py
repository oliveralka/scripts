#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Sep 22 10:04:02 2017

Intended to merge mzTab files as they are produces by SIRIUS or CSI:FingerID.
The first inputfile is simply copied to the output file. For all remaining
input files, all lines with SML records are appended to the output file.

@author: Lukas Zimmermann
"""
from __future__ import division
import sys
import argparse
import os


def main(argv):
    
    # Argument parser
    parser = argparse.ArgumentParser()
    
    parser.add_argument('-i', type=argparse.FileType('r'), nargs='+', help="MzML Files to be merged.", required=True)
    parser.add_argument('-o', type=argparse.FileType('w'), help="Where the result should be written to", required=True)
    parser.add_argument('--prefix', type=str, help="Lines starting with this prefix are going to be appended to the original file", required=True)
    args = parser.parse_args(argv[1:])
    infiles = args.i
    prefix = args.prefix.strip()
    
    try:
        with args.o as outfile:
            
            # Copy whole content of  first file
            infiles = args.i
            
            with infiles[0] as infile:
                for line in infile:
                    line = line.strip()
                    if not line:
                        continue
                    outfile.write(line)
                    outfile.write(os.linesep)
                   
            for infile in infiles[1:]:
                with infile as infile:
                    for line in infile:
                        line = line.strip()
                        if line.startswith(prefix):
                            outfile.write(line)
                            outfile.write(os.linesep)
     
    # If something goes wrong, delete the output file, so the 
    # user is not presented with an incomplete file
    except:
        os.remove(outfile.name)
        return 1
        
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
