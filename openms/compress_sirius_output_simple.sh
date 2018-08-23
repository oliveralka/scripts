#!/bin/bash
"""
Created on Fri Aug 23

Compress sirius output 
first argument = output file (e.g. archive.zip)
second argument = all files that should be zipped (e.g. *)

@author: Oliver Alka 
"""

zip -j $1 ${@:2}
