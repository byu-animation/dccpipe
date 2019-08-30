#!/bin/sh
SOURCEDIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
source $SOURCEDIR/env.sh
export CURRENT_PROGRAM='manager'

export PYTHONPATH="/opt/hfs17.0.352/python/lib/python2.7/site-packages-ui-forced":${PYTHONPATH}

echo "Starting Manager..."
python pipe/app/manager/main.py
