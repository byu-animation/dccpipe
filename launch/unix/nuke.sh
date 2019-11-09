#!/bin/sh
SOURCEDIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
source $SOURCEDIR/env.sh
export CURRENT_PROGRAM='nuke'

# Change directories so current directory is not in the tools folder
cd ${USER_DIR}

export ICONS_DIR=${MEDIA_PROJECT_DIR}'/pipe/tools/_resources/'
export NUKE_LOCATION=/opt/Nuke11.3v5/Nuke11.3
export NUKE_TOOLS_DIR=${MEDIA_PROJECT_DIR}'/pipe/tools/nuketools/'
export NUKE_PATH=${NUKE_TOOLS_DIR}
export DCC_NUKE_ASSET_NAME=''

alias nuke=${NUKE_LOCATION}

# change to home directory
cd

echo "Starting Nuke..."
# gnome-terminal -e "${NUKE_LOCATION} $@"
# cd -

nuke
