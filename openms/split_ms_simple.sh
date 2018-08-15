#!/bin/bash
"""
Created on Fri Aug 15

Split sirius internal .ms file after n compound entries
first argument = file 
second argument = number of compounds counted for split

@author: Oliver Alka 
"""

awk '/>compound/ { delim++ } { file = sprintf("%s.ms", int(delim / '$2')); print >> file; }' $1 
