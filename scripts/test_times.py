#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
import sys

def regex_line_parser(pattern, handler):
    regex = re.compile(pattern)
    def parser(line):
        match = regex.match(line)
        if match:
            return handler(match)
        return None
    return parser

def rstripped(match):
    return match.group(0).rstrip()

def tupled(match):
    return (match.group(1), match.group(2))


def parse(lines):
    test_file = None
    timing = None
    test_file_timings = []

    test_file_line_parser = regex_line_parser('.*?Test.py', rstripped)
    timing_line_parser = regex_line_parser('Ran (.*) tests in (.*)', tupled)

    for line in lines:
        if test_file is None:
            test_file = test_file_line_parser(line)
        elif timing is None:
            timing = timing_line_parser(line)

        if test_file is not None and timing is not None:
            test_file_timings.append((test_file, timing))
            test_file = None
            timing = None

    return test_file_timings

def report(parsed_data):
    lines = [
        '| Method | Time | Tests Ran |',
        '|----|----|----|',
    ]

    sorted_data = sorted(parsed_data, key=lambda d: d[1][1], reverse=True)
    for d in sorted_data:
        lines.append(f'| {d[0]} | {d[1][1]} | {d[1][0]} |')

    print('\n'.join(lines))

if __name__ == '__main__':
    data = sys.stdin.readlines()
    parsed_data = parse(data)
    report(parsed_data)
