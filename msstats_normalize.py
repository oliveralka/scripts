#!/usr/bin/env python3
"""
This script is intended to normalize MSstats input CSV such that
it can be compared among multiple producers
"""
import argparse
import sys


def normalize_intensity(intensity):
    return "{0:.2f}".format(float(intensity))


def main():
    # Constants
    SEP = ','

    parser = argparse.ArgumentParser()
    parser.add_argument('-i', type=str, required=True)
    parser.add_argument('-o', type=str, required=True)
    args = parser.parse_args(sys.argv[1:])

    with open(args.i, 'r') as f:
        with open(args.o, 'w') as outfile:
            header = False
            headers = {}
            header_order = []
            for line in f:
                line = line.strip()
                if not line:
                    continue
                if not header:
                    if 'ProteinName' in line:
                        header = True
                        outfile.write(line + '\n')
                        header_order = line.split(SEP)
                        # Match headers to column index
                        headers = { column: index for (index, column) in enumerate(header_order)}
                    else:
                        print("FATAL: CSV input file does not start with header",
                              file=sys.stderr)
                        sys.exit(1)
                else:
                    # Map the content of the line to a dict with the column names
                    # as key names
                    spt = line.split(SEP)
                    line_content = {  header: spt[headers[header]]  for header in headers.keys() }
                    line_content['Intensity'] = normalize_intensity(line_content['Intensity'])
                    outfile.write(SEP.join([ line_content[header] for header in header_order]) + '\n')




if __name__ == '__main__':
    main()
