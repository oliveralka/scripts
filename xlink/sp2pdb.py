#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Mar 13 19:32:07 2017

Translates swissprot (sp) identifier within a FASTA file into PDB
accessions and also allows downloading them into a directory

@author: lzimmermann
"""
import argparse
import sys



def main(argv):
    
    parser = argparse.ArgumentParser()
    parser.add_argument("IN", type=str)
    args = parser.parse_args(argv[1:])
    
    



if __name__ == '__main__':
    main(sys.argv)