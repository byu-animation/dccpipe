#!/bin/sh
SOURCEDIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
source $SOURCEDIR/env.sh

# This isn't the most robust script, but it's better than hard-coding the path
TRACTOR_LOCATION="`locate pixar/Tractor | head -n 1`"
TRACTOR_AUTHOR=${TRACTOR_LOCATION}/lib/python2.7/site-packages
export PYTHONPATH=${PYTHONPATH}:${TRACTOR_AUTHOR}
