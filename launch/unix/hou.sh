#!/bin/sh
SOURCEDIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
source $SOURCEDIR/env.sh
export CURRENT_PROGRAM='hou'

# Will find the installation of Houdini on the PATH if $HFS is not set
if [ ! $HFS ]
then
  hfs_location=("`which houdini`")
  if [ -z $hfs_location ]
  then
    echo "No houdini command found on the PATH."
    return -1
  fi
  hou_binary=$(realpath $hfs_location)
  export HFS="$(cd "$( dirname "${hou_binary}" )" && cd ../ && pwd )"
fi

# source current houdini setup
cd ${HFS}
source ./houdini_setup
cd -

# We need this line in order for gridmarkets to work.
export HOUDINI_USE_HFS_PYTHON=1
export JOB=${MEDIA_PROJECT_DIR}
HOUDINI_TOOLS=${MEDIA_PROJECT_DIR}/pipe/tools/houtools
export PYTHONPATH=${PYTHONPATH}:${HOUDINI_TOOLS}
export HOUDINI_PATH=${HOUDINI_PATH}:${HOUDINI_TOOLS}"/_custom;&":${HOUDINI_TOOLS}:${MEDIA_PROJECT_DIR}"/production;&":${MEDIA_PROJECT_DIR}"/production/hda;&"
export HOUDINI_DSO_PATH=${HOUDINI_DSO_PATH}:${MEDIA_PROJECT_DIR}"/production/dso;&"

export HOUDINI_MENU_PATH=${HOUDINI_TOOLS}"/_custom/menus;&"
export HOUDINI_TOOLBAR_PATH=${MEDIA_PROJECT_DIR}"/production/tabs;&"
export HOUDINI_UI_ICON_PATH=${MEDIA_PROJECT_DIR}"/pipe/tools/_resources/tool-icons;&"

echo "Starting Houdini..."
cd ~/
gnome-terminal -e "houdinifx -foreground $@"
cd -
