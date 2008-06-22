#!/usr/bin/python
import os, sys, unittest

modules = ['DBTest',
           'DriverTest',
           'JobInfoTest',
           'TaskInfoTest',
           'WorkflowInfoTest']

# Parse CLI options.
if len(sys.argv) == 1:
    verbosity = 2
elif len(sys.argv) == 2:
    verbosity = int(sys.argv[1])
else:
    print 'Syntax:', sys.argv[0], '[verbosity]'
    print 'Default verbosity is 2'
    sys.exit(1)

# Load all test suites.
all_suites = []
for name in modules:
    module = __import__(name, globals(), locals(), [''])
    all_suites.append(module.suite())

# Run.
suite = unittest.TestSuite(all_suites)
unittest.TextTestRunner(verbosity = verbosity).run(suite)
