#!/bin/sh

# The location of your yuidoc install
yuidoc_home=~/Tools/yuidoc

# The location of your inputEx project
INPUTEXPATH="$HOME/Projets/inputex/master"

# The location of the files to parse.  Parses subdirectories, but will fail if
# there are duplicate file names in these directories.  You can specify multiple
# source trees:
#     parser_in="%HOME/www/yui/src %HOME/www/event/src"
parser_in="$INPUTEXPATH/js"

# The location to output the parser data.  This output is a file containing a 
# json string, and copies of the parsed files.
parser_out="$INPUTEXPATH/scripts/doc-parser"

# The directory to put the html file outputted by the generator
generator_out="$INPUTEXPATH/api"

# The location of the template files.  Any subdirectories here will be copied
# verbatim to the destination directory.
template="$yuidoc_home/template"

# The version of your project to display within the documentation.
version=0.5.1

# The version of YUI the project is using.  This effects the output for
# YUI configuration attributes.  This should start with '2' or '3'.
yuiversion=2.8.0r4

projectName="inputEx-library"

projectUrl="http://neyric.github.com/inputex"

##############################################################################
# add -s to the end of the line to show items marked private

$yuidoc_home/bin/yuidoc.py $parser_in -p $parser_out -o $generator_out -t $template -v $version -Y $yuiversion --project $projectName --projecturl $projectUrl --copyright="Eric Abouaf"
rm -rf $parser_out