#!/bin/sh

SOURCEDIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
LAUNCHDIR=$SOURCEDIR
while [ $(basename $LAUNCHDIR) != "/" ] && [ $(basename $LAUNCHDIR) != "launch" ]
do
  LAUNCHDIR="$(dirname "$LAUNCHDIR")"
done

INIT_SCRIPT="$(dirname "$LAUNCHDIR")/config/unix/init_all_env.sh"
source $INIT_SCRIPT

export PYTHONPATH=${PYTHONPATH}:${MEDIA_PIPE_DIR}

echo "Initialized BYUPipe environment."
