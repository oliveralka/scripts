#!/bin/bash
"""
Created on Fri Aug 15

Compress sirius output 
first argument = output file (e.g. archive.zip)
second argument = all files that should be zipped (e.g. *)

@author: Oliver Alka 
"""

zip $1 ${@:2}
