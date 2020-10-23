#!/bin/sh
SOURCEDIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
source $SOURCEDIR/env.sh
export CURRENT_PROGRAM='nuke'

# Change directories so current directory is not in the tools folder
cd ${USER_DIR}

export ICONS_DIR=${MEDIA_PROJECT_DIR}'/pipe/tools/_resources/'
export NUKE_LOCATION="/opt/Nuke12.2v3/Nuke12.2 --nukex"
export NUKE_TOOLS_DIR=${MEDIA_PROJECT_DIR}'/pipe/tools/nuketools/'
export NUKE_PATH=${NUKE_TOOLS_DIR}
export DCC_NUKE_ASSET_NAME=''

alias nuke=${NUKE_LOCATION}

# change to home directory
cd

echo "Starting Nuke..."

nuke

# try other path for monsters
export NUKE_LOCATION_2="/usr/local/Nuke11.2v5/Nuke11.2 --nukex"
alias nuke_monster=${NUKE_LOCATION_2}
nuke_monster
