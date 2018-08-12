#!/usr/bin/env python
import argparse
import os
import sys


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('FILE', type=str)
    args = parser.parse_args()

    if not os.path.isfile(args.FILE):
        print("FATAL: Input file must be regular file", file=sys.stderr)
        sys.exit(1)

    with open(args.FILE, 'r') as infile:
        lines = [ line for line in infile if line.strip() ]

    n_lines = len(lines)
    # Output new lines
    def print_line(line, pipe, last=False):
        line = line.strip()
        result = "'{}' {} {} ".format(line, pipe, args.FILE)
        end = '&& sync' if last else '\\'
        print(result + end)

    if n_lines == 1:
        print_line(lines[0], '>', last=True)
    elif n_lines > 1:
        print_line(lines[0], '>', last=False)
        for line in lines[1:-1]:
            print_line(line, '>>', last=False)
        print_line(lines[-1], '>>', last=True)

if __name__ == '__main__':
    main()
