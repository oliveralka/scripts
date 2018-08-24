#!/usr/bin/env python
"""
Renumbers the ranks of of the hits in an xQuest result file according
to the order within the spectrum
"""
import re
import sys

def main():

    try:
        rank = 1
        re_rank = re.compile(r'search_hit_rank="([0-9]+)"')

        with open(sys.argv[1], 'r') as f:
            for line in f:
                if line.startswith("<search_hit "):
                    line = re.sub(re_rank, 'search_hit_rank="{}"'.format(rank),line)
                    rank += 1
                elif line.startswith("</spectrum_search"):
                    rank = 1
                sys.stdout.write(line)
    finally:
        sys.stdout.close()
if __name__ == '__main__':
    main()

