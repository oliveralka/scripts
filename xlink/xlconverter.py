#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Mar 11 15:56:39 2017

Converts output files with Cross-Link information in different file formats


@author: lzimmermann
"""
import argparse
import os
import sys
import re
from Bio import SeqIO


def getAttFromLine(line):
    """
    Returns a dictionary with key value pairs from a line with XML markup
    """
    return  {q[0]: q[1][1:-1].strip() for q in  (pair.split("=") for pair in line.split()[1:])}


max_fdr = 1
xprop_flagged = False

def xquest2xlinkanalyzer(infile, database_index, modres):
    global xprop_flagged
    global max_fdr
    
    with open(infile, 'r') as f:
        print("Id,Protein1,Protein2,AbsPos1,AbsPos2,score")
        for line in f:
            line = line.strip()
            if line.startswith('<search_hit'):
                d = getAttFromLine(line)
                
                # Ignore decoy sequences
                if 'decoy' in d['prot1'] or 'decoy' in d['prot2']:
                    continue          
                                
                # get crosslink position
                xlpos = d['xlinkposition']
                if xlpos.endswith('"'):
                    xlpos = xlpos[:-1]
                xlpos = xlpos.split(',')
                
                # Handle first protein
                prot1_seq = str(database_index[d['prot1']].seq)
                pep1_seq = d['seq1'].replace('X', modres).replace('x', modres)
                
                # match first peptide
                abspos1 = '+'.join([str(m.start() + int(xlpos[0])) 
                for m in re.finditer(pep1_seq, prot1_seq)])
                
                prot2 = d['prot2'].strip()
                if prot2:
                    prot2_seq = str(database_index[prot2].seq)
                    pep2_seq = d['seq2'].replace('X', modres).replace('x', modres)
                    abspos2 = '+'.join([str(m.start() + int(xlpos[1])) for m in re.finditer(pep2_seq, prot2_seq)])                    
                else:
                    abspos2 = '-'
                    prot2 = '-'
                    
                if 'fdr' in d:
                    fdr = float(d['fdr'])
                else:
                    fdr = 0

                if  fdr > max_fdr:
                    continue
                
                # XProphet flagged
                xprophet_f = d["xprophet_f"]
                if xprophet_f.endswith('"'):
                    xprophet_f = xprophet_f[:-1]
                
                if int(xprophet_f) == 0 and xprop_flagged:
                    continue
        
                print(','.join([d['id'], d['prot1'].strip(), 
                                prot2, abspos1, abspos2, d['score']]))
            
def checkfile(filepath):
    
    if not os.path.isfile(filepath):
        sys.stderr.write("ERROR: File: {} does not exist.\n".format(filepath))
        return False
    return True
    
def detect_format(infile):
    with open(infile, 'r') as f:
        for line in f:
            line = line.strip()
            if line.startswith("<xquest"):
                return "xquest"
    return None                
    

def xquest2xinet(infile, database_index):
    global xprop_flagged
    global max_fdr
    
    with open(infile, 'r') as f:
        print('Score,Protein1,LinkPos1,Protein2,LinkPos2')   
        for line in f:
            line = line.strip()
            if line.startswith('<search_hit'):
    
                d = getAttFromLine(line)
                link_pos = d['xlinkposition'].split(',')
                lpos2 = link_pos[1] if len(link_pos) == 2 else ""      
                print(','.join([str(float(d['score'])),
                                          d['prot1'],
                                          link_pos[0].replace('"', ''),
                                          d['prot2'],
                                          lpos2.replace('"','')]))
                
def main(argv):
    global max_fdr
    global xprop_flagged
    
    
    allowed_output_formats = ['xinet', 'xlinkanalyzer']
    allowed_fasta_endings = ['fasta', 'fa', 'fas']

    parser = argparse.ArgumentParser()
    parser.add_argument('IN', type=str)
    parser.add_argument('-f', metavar="FORMAT", type=str, required=True)
    parser.add_argument('-d', metavar="DB", type=str, required=True)
    parser.add_argument('-m', metavar="MOD", type=str, required=True)
    parser.add_argument('--xproph', dest='xproph', action='store_true')
    parser.add_argument('--fdr', metavar="FDR", type=float)
    
    args = parser.parse_args(argv[1:])
    
    if args.f not in allowed_output_formats:
        sys.stderr.write('ERROR: Output file format unknown\n')
        sys.exit(2)
    
    if not checkfile(args.IN) or not checkfile(args.d):
        sys.stderr.write("ERROR: Cannot continue due to previous error\n")
        sys.exit(1)
    
    if sum([ args.d.endswith(x) for x in allowed_fasta_endings]) != 1:
        sys.stderr.write("Unknown file ending of database. Terminating\n")
        sys.exit(3)
        
    formt = detect_format(args.IN)
    if formt is None:
        sys.stderr.write("ERROR: Input format of xl file could not be determined\n")
        sys.exit(2)

    if len(args.m) != 1:
        sys.stderr.write("ERROR: Please specify only one character for the variable modification\n")
        sys.exit(4)
        
    if args.fdr is not None:    
        max_fdr = args.fdr 
    xprop_flagged = args.xproph

    # Create index of database
    database_index = SeqIO.index(args.d, "fasta")
   

    if formt == "xquest" and args.f == "xinet":
        xquest2xinet(args.IN, database_index)
    elif formt == "xquest" and args.f == "xlinkanalyzer":
        xquest2xlinkanalyzer(args.IN, database_index, args.m.upper())


    sys.stdout.close()
    sys.stderr.close()
    database_index.close()
        

if __name__ == '__main__':
    main(sys.argv)

