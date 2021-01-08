#!/bin/sh
SOURCEDIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
echo "$SOURCEDIR"
source $SOURCEDIR/env.sh
export CURRENT_PROGRAM='hou'

# Will find the installation of Houdini on the PATH if $HFS is not set
if [ ! $HFS ]
then
  #echo "$HFS"
  hfs_location=("`which houdini`")
  echo "$hfs_location"
  if [ -z $hfs_location ]
  then
    echo "No houdini command found on the PATH."
    return -1
  fi
  hou_binary=$(realpath $hfs_location)
  #use this if you want to use a specific version of houdini
  #hou_binary="/opt/hfs18.0.532/bin/houdini"
  echo "$hou_binary"
  export HFS="$(cd "$( dirname "${hou_binary}" )" && cd ../ && pwd )"
  echo "$HFS"
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
export HOUDINI_PATH=${HOUDINI_PATH}:${HOUDINI_TOOLS}"/_custom;&":${HOUDINI_TOOLS}:${MEDIA_PROJECT_DIR}"/production;&":${MEDIA_PROJECT_DIR}"/production/hdas;&"
export HOUDINI_DSO_PATH=${HOUDINI_DSO_PATH}:${MEDIA_PROJECT_DIR}"/production/dso;&"

export HOUDINI_MENU_PATH=${HOUDINI_TOOLS}"/_custom/menus;&"
export HOUDINI_TOOLBAR_PATH=${MEDIA_PROJECT_DIR}"/production/tabs;&"
export HOUDINI_UI_ICON_PATH=${MEDIA_PROJECT_DIR}"/pipe/tools/_resources/tool-icons;&"

# Renderman paths (Renderman 22) for use with Hou 17.5
# FIXME: This is now going to be obsolete for houdini 18
#export RMANTREE="/opt/pixar/RenderManProServer-22.6"
#export RFHTREE="/opt/pixar/RenderManForHoudini-22.6"
#export RMAN_PROCEDURALPATH=$RFHTREE/18.0.532/openvdb:&
#export HOUDINI_PATH=${HOUDINI_PATH}:$RFHTREE"/17.5:&"

#export RMANTREE="/opt/pixar/RenderManProServer-23.4"
#export RFHTREE="/opt/pixar/RenderManForHoudini-23.4"
#export RMAN_PROCEDURALPATH=$RFHTREE/18.0.532/openvdb:&
#export HOUDINI_PATH=${HOUDINI_PATH}:$RFHTREE"/18.0.532:&"

export RMANTREE="/opt/pixar/RenderManProServer-23.5"
export RFHTREE="/opt/pixar/RenderManForHoudini-23.5"
export RMAN_PROCEDURALPATH=$RFHTREE/18.5.351/openvdb:&
export HOUDINI_PATH=${HOUDINI_PATH}:$RFHTREE"/18.5.351:&"

# set current houdini path for installation
# hou_launch_path=`python -c "import json; print json.load(file('.settings'))['hou_launch_path']"`

echo "Starting Houdini..."
cd ~/
gnome-terminal -e "houdinifx -foreground $@"
# gnome-terminal -e ${DCC_HOUDINI_LAUNCH_PATH}" -foreground $@"
cd -
$SHELL
