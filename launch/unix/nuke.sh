#!/bin/sh
SOURCEDIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
source $SOURCEDIR/env.sh
export CURRENT_PROGRAM='nuke'

# Change directories so current directory is not in the tools folder
cd ${USER_DIR}

echo "Starting Nuke..."
${NUKE_LOCATION}/Nuke10.0 -b --nukex
