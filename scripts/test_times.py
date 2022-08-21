#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
import sys

def parse(lines):
    test_file = None
    timing = None

    test_file_regex = re.compile('.*?Test.py')
    timing_regex = re.compile('Ran .* tests in .*')

    for line in lines:
        # line.rstrip()
        if test_file is None:
            match = test_file_regex.match(line)
            if match:
                test_file = match.group(0).rstrip()
        elif timing is None:
            match = timing_regex.match(line)
            if match:
                timing = match.group(0).rstrip()

        if test_file is not None and timing is not None:
            print(f'{test_file}: {timing}')
            test_file = None
            timing = None

if __name__ == '__main__':
    data = sys.stdin.readlines()
    parse(data)
