#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Mar  3 11:08:41 2017


Calculates the euclidean distance between pairs of residues.

@author: lzimmermann
"""
import sys
import argparse
import os
import math

def extract(segment, t):
    def from_line(line):
        if isinstance(segment, tuple):
            return t(line[segment[0]-1:segment[1]].strip())
        else:
            return t(line[segment-1].strip())
    return from_line
# Line extractors for legacy pdb format for particular fields
record_atom_resid = extract((23, 26), str)
record_atom_segid = extract(22, str)
record_atom_resname = extract((18, 20), str)
record_atom_name = extract((13, 16), str)
record_atom_x = extract((31, 38), float)
record_atom_y = extract((39, 46), float)
record_atom_z = extract((47, 54), float)


def checkfile(filename, extension=None):
    """
    Checks whether file designated by filename exists and whether it
    has the required extension. 
    
    Prints error message to stderr and return False on failure.
    """
    if not os.path.isfile(filename):
        sys.stderr.write("File {} does not exist.{}".format(filename, os.linesep))
        return False
    
    # Done if we do not care about the extension
    if extension is None:
        return True
    
    # Get file extension
    true_extension = filename.split('.')[-1]
    if extension != true_extension:
        sys.stderr.write("File {} does not have the correct extension.{}Expected: {}{}Have:{}{}".format(filename, os.linesep, extension, os.linesep, extension, os.linesep ))
        return False
    return True
    

# Writes the results back as CSV
def write_results_csv(filename, dist_lookup):
    """
    Generates the Residues within a CSV file assuming a given order.
    """    
    import csv
    with open(filename, 'r') as csvfile_handle:
        for row in csv.reader(csvfile_handle, delimiter=','):
            key = tuple([item.strip() for item in row[:8]])
            if key in dist_lookup:
                    row.append(str(dist_lookup[key]))
            sys.stdout.write(','.join(row) + os.linesep)


def generate_residues_csv(filename):
    """
    Generates the Residues within a CSV file assuming a given order.
    """
    # Attention: Order of residue attributes is assumed here
    names = ['resid1', 'resname1', 'atomname1', 'segid1', 'resid2', 'resname2', 'atomname2', 'segid2']
    import csv
    with open(filename, 'r') as csvfile_handle:
        for row in csv.reader(csvfile_handle, delimiter=','):
            if len(row) < 8:
                sys.stdout.write("Not enough fields for row. Skipping..{}".format(os.linesep))
                continue            
            # Attention: Order of residue attributes is assumed here
            yield dict(zip(names, [item.strip() for item in row[:8]]))

def generate_residues_pdb(filename):
    """
    Generates the residues within a PDB file.
    """
    with open(filename, 'r') as pdbfile_handle:
        for line in pdbfile_handle:   
            if line.startswith("ATOM"):
                yield {
                    'resid':    record_atom_resid(line),
                    'segid':    record_atom_segid (line),
                    'resname':  record_atom_resname(line),
                    'atomname': record_atom_name(line),
                    'x': record_atom_x(line),
                    'y': record_atom_y(line),
                    'z': record_atom_z(line)
                  }
    
    
def dot_product(x, y):
    return sum((a*b for (a,b) in zip(x,y)))


def vec_norm(x):
    return math.sqrt(dot_product(x,x))
    

def main(argv):
    
    parser = argparse.ArgumentParser(description="Computes Euclidean distances within a protein between pairs of residues")
    parser.add_argument("IN_PDB",  type=str)
    parser.add_argument("IN_DIST", type=str)
    
    args = parser.parse_args(argv[1:])

    if not checkfile(args.IN_PDB, "pdb") or not checkfile(args.IN_DIST):
         sys.stderr.write("Cannot continue due to previous errors.{}".format(os.linesep))
         sys.exit(1)
        
    # Handle distfile in csv format and construct filter for the pdbfile
    if args.IN_DIST.endswith("csv"):
        filter_residues = list(generate_residues_csv(args.IN_DIST))
    else:
        sys.stderr.write("Unsupported file extension for the distfile. Terminating.{}".format(os.linesep))
        
 
    def join(x):
        for residue in filter_residues:
            if residue["resname1"] == x["resname"] and residue["segid1"] == x["segid"] and residue["resid1"] == x["resid"] and residue["atomname1"] == x["atomname"]:
                residue["x1"] = x['x']
                residue["y1"] = x['y']
                residue["z1"] = x['z']
                
            if residue["resname2"] == x["resname"] and residue["segid2"] == x["segid"] and residue["resid2"] == x["resid"] and residue["atomname2"] == x["atomname"]:
                residue["x2"] = x['x']
                residue["y2"] = x['y']
                residue["z2"] = x['z']
    
    # Joins all residues in the PDB File to the residues in the filter_residues list
    for residue in generate_residues_pdb(args.IN_PDB):
            join(residue)        
    
    dict_lookup = {}        
    for residue in filter_residues:
        if "x1" in residue and "y1" in residue:
            dict_lookup[(residue["resid1"],residue["resname1"],residue["atomname1"],residue["segid1"],
                         residue["resid2"],residue["resname2"],residue["atomname2"],residue["segid2"])] = vec_norm([a-b for (a,b) in zip([residue["x1"], residue["y1"], residue["z1"]], 
                                                  [residue["x2"], residue["y2"], residue["z2"]])])         
            
    # Handle distfile in csv format and construct filter for the pdbfile
    if args.IN_DIST.endswith("csv"):
        write_results_csv(args.IN_DIST, dict_lookup)


        
if __name__ == '__main__':
    main(sys.argv)