#!/bin/sh

SOURCEDIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
CONFIGDIR=$SOURCEDIR
while [ $(basename $CONFIGDIR) != "/" ] && [ $(basename $CONFIGDIR) != "config" ]
do
  CONFIGDIR="$(dirname "$CONFIGDIR")"
done

source $CONFIGDIR/unix/init_media_env.sh
source $MEDIA_PROJECT_DIR/.venv/bin/activate
source $CONFIGDIR/unix/init_media_env.sh
source $CONFIGDIR/unix/init_pyside_env.sh
