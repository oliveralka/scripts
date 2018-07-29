#!/usr/bin/env python3

## Rewrites the OpenMS CMakeLists file from Dynamic to static linking
import argparse

static = '''
SET(CMAKE_FIND_LIBRARY_SUFFIXES ".a")
SET(BUILD_SHARED_LIBS OFF)
SET(CMAKE_EXE_LINKER_FLAGS "-static")
'''

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", type=str, required=True)    
    parser.add_argument("-o", type=str, required=True)
    args = parser.parse_args()
    with open(args.i, 'r') as inhandle:
        with open(args.o, 'w') as outhandle:
            for line in inhandle:
                line = line.strip()
                if line.startswith("project"):
                    line = line + static
                elif 'BUILD_SHARED_LIBS' in line:
                    line = 'set(BUILD_SHARED_LIBS false)'
                outhandle.write(line + '\n')

if __name__ == '__main__':
    main()

