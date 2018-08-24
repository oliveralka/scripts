#!/usr/bin/env python
"""
Spits out the ranks of each search hit for a xQuest result file grouped by
the spectra

"""
import re
import sys

def main():

    re_rank = re.compile(r'search_hit_rank="([0-9]+)"')

    with open(sys.argv[1], 'r') as f:
        for line in f:
            if line.startswith("<search_hit "):
                m = re.findall(re_rank, line)
                print(m[0])
            elif line.startswith("</spectrum_search"):
                print("===")


if __name__ == '__main__':
    main()

