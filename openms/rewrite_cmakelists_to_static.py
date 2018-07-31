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
    parser.add_argument("infile", type=str)
    args = parser.parse_args()

    lines = []
    with open(args.infile, 'r') as inhandle:
        for line in inhandle:
            if line.startswith('project'):
                line = line + static
            elif 'BUILD_SHARED_LIBS' in line:
                line = 'set(BUILD_SHARED_LIBS false)\n'
            lines.append(line)
    with open(args.infile, 'w') as outhandle:
        for line in lines:
            outhandle.write(line)


if __name__ == '__main__':
    main()

