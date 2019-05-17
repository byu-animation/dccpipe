#!/bin/sh
if [ $DCC_PIPE_LOADED ] && [ $DCC_PIPE_LOADED -ne 1 ]
then
  return 1
fi

SOURCEDIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
LAUNCHDIR=$SOURCEDIR
while [ $(basename $LAUNCHDIR) != "/" ] && [ $(basename $LAUNCHDIR) != "launch" ]
do
  LAUNCHDIR="$(dirname "$LAUNCHDIR")"
done

SHELL_SCRIPT="$(dirname "$LAUNCHDIR")/config/unix/shell.sh activate"
ENV_SCRIPT="$(dirname "$LAUNCHDIR")/config/unix/env.sh"
source $SHELL_SCRIPT
source $ENV_SCRIPT

export PYTHONPATH=${PYTHONPATH}:${MEDIA_PROJECT_DIR}:${MEDIA_PIPE_DIR}

export DCC_PIPE_LOADED=1

echo "Initialized dccpipe environment."
