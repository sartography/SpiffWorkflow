#!/usr/bin/env python
# Generates the API documentation.
import os, re, sys

doc_dir  = 'api'
doc_file = os.path.join(doc_dir, 'Spiff_Workflow.py')
files    = ['../src/SpiffWorkflow/Task.py',
            '../src/SpiffWorkflow/Job.py',
            '../src/SpiffWorkflow/Tasks/TaskSpec.py',
            '../src/SpiffWorkflow/Tasks/Join.py'] # Order matters - can't resolve inheritance otherwise.
classes  = [os.path.splitext(os.path.basename(file))[0] for file in files]
classes  = ['(?:SpiffWorkflow.)?' + cl for cl in classes]

# Concatenate the content of all files into one file.
if not os.path.exists(doc_dir):
    os.makedirs(doc_dir)
remove_re = re.compile(r'^from (' + '|'.join(classes) + r') * import .*')
fp_out    = open(doc_file, 'w')
for file in files:
    fp_in = open(file, 'r')
    for line in fp_in:
        if not remove_re.match(line):
            fp_out.write(line)
    fp_in.close()
fp_out.close()

os.system('epydoc ' + ' '.join(['--html',
                                '--parse-only',
                                '--no-private',
                                '--no-source',
                                '--no-frames',
                                '--fail-on-error',
                                '--inheritance=grouped',
                                '-v',
                                '-o %s' % doc_dir, doc_file]))
