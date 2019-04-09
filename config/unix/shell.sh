#!/bin/sh

SOURCEDIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
CONFIGDIR=$SOURCEDIR
while [ $(basename $CONFIGDIR) != "/" ] && [ $(basename $CONFIGDIR) != "config" ]
do
  CONFIGDIR="$(dirname "$CONFIGDIR")"
done

export MEDIA_PROJECT_DIR="$(dirname "$CONFIGDIR")"

if [ $1 == "activate" ]
then
  source $MEDIA_PROJECT_DIR/.venv/bin/activate
  export MEDIA_SUBSHELL_ACTIVE=1
elif [ $1 == "deactivate" ]
then
  deactivate
else
  echo "Usage: shell.sh activate | deactivate"
fi
