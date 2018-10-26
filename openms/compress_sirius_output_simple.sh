#!/bin/bash

<<COMMENT
Created on Fri Aug 23

Compress sirius output 
first argument = output file (e.g. archive.zip)
second argument = all files that should be zipped (e.g. *)

@author: Oliver Alka
COMMENT

# do not use j since sirius workspace is not unique
zip -r $1 ${@:2} 
