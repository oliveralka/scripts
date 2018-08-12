#!/usr/bin/env python
import argparse
import os
import sys


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('FILE', type=str)
    parser.add_argument('-c', type=str, required=False)
    args = parser.parse_args()

    if not os.path.isfile(args.FILE):
        print("FATAL: Input file must be regular file", file=sys.stderr)
        sys.exit(1)

    comment_prefix = args.c
    not_use_comment = args.c is None

    with open(args.FILE, 'r') as infile:
        lines = [ line for line in infile
                    if line.strip() and (not_use_comment or not line.startswith(comment_prefix))]

    n_lines = len(lines)
    # Output new lines
    def print_line(line, pipe, last=False):
        line = line.strip()
        result = "echo '{}' {} {} ".format(line, pipe, args.FILE)
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
