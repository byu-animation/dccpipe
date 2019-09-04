#!/bin/sh
SOURCEDIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
source $SOURCEDIR/env.sh
export CURRENT_PROGRAM="sbs"

export SUBSTANCE_PLUGINS_DIR=${MEDIA_PROJECT_DIR}'/pipe/tools/sbstools/_custom/'
export SUBSTANCE_ICONS_DIR=${MEDIA_PROJECT_DIR}'/pipe/tools/_resources/'

echo "Starting Substance..."
substancepainter
