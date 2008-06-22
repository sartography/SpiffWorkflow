#!/bin/sh
find . -name "run_suite.py" | while read i; do
  echo $i
  cd `dirname $i`
  python `basename $i`
  cd - >/dev/null
done
