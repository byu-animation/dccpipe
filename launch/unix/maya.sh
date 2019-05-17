#!/bin/sh
SOURCEDIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
source $SOURCEDIR/env.sh
export CURRENT_PROGRAM='maya'

export MAYA_SHELF_DIR=${MEDIA_PROJECT_DIR}'/pipe/tools/maya/_custom/'
export MAYA_ICONS_DIR=${MEDIA_PROJECT_DIR}'/pipe/tools/_resources/'

echo "Starting Maya..."
maya -script ${MEDIA_PROJECT_DIR}/pipe/tools/maya/_custom/shelf.mel &
