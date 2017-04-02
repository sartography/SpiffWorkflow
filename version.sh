#!/bin/sh
# Tag revisions like this:
# $ git tag -a -m "v0.2" v0.2
VERSION_IN=VERSION.in
VERSION_FILE=SpiffWorkflow/version.py

# Check that we are actually in a git managed project.
if [ ! -e .git -a -z "$1" ]; then
  echo >&2 Not a git repository.
  exit 1
fi

# Make sure that we have permission to modify the version file.
if [ -r $VERSION_FILE -a ! -w $VERSION_FILE ]; then
  echo >&2 No permission to modify $VERSION_FILE.
  exit 1
fi

# By default, get the version number from "git describe".
if [ ! -z "$1" ]; then
  VERSION=$1
else
  HEAD=`git log -1 --pretty=format:%H HEAD`
  VERSION=`git describe $HEAD --tags --match "v[0-9]*" | sed 's/^v//;s/-[^\-]*$//;s/-/./' 2>/dev/null`
  if [ -z "$VERSION" ]; then
    echo >&2 No matching tag was found.
    exit 1
  fi
fi

# If the --reset switch was given, reset the version number to 'DEVELOPMENT'.
[ "$1" = "--reset" ] && VERSION='DEVELOPMENT'

# If there is no version file, we are already done.
echo Version is $VERSION
[ ! -r $VERSION_FILE ] && exit 0

# Check whether the version file already contains this number,
# and only touch it if there is a change to avoid changing
# the timestamp.
VERSION_FILE_TMP=`mktemp`
cat $VERSION_IN | sed "s/@VERSION@/$VERSION/g" > $VERSION_FILE_TMP
if diff -q $VERSION_FILE_TMP $VERSION_FILE; then
  echo Version file unchanged.
  rm $VERSION_FILE_TMP
  exit 0
fi

mv $VERSION_FILE_TMP $VERSION_FILE
echo Version file updated.
