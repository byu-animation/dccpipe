#!/bin/sh

SOURCEDIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
source $SOURCEDIR/env.sh

export CURRENT_PROGRAM='maya'

echo "Starting Maya..."
maya -script ${MEDIA_PROJECT_DIR}/pipe/tools/maya/_custom/shelf.mel &
