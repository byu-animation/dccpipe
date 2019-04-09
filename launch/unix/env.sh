#!/bin/sh

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

export PYTHONPATH=${PYTHONPATH}:${MEDIA_PIPE_DIR}

echo "Initialized byupipe environment."
