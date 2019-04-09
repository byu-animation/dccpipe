#!/bin/sh

SOURCEDIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
CONFIGDIR=$SOURCEDIR
while [ $(basename $CONFIGDIR) != "/" ] && [ $(basename $CONFIGDIR) != "config" ]
do
  CONFIGDIR="$(dirname "$CONFIGDIR")"
done

export MEDIA_PROJECT_DIR="$(dirname "$CONFIGDIR")"
export MEDIA_DOCS_DIR=$MEDIA_PROJECT_DIR/docs
export MEDIA_LAUNCH_DIR=$MEDIA_PROJECT_DIR/launch
export MEDIA_PIPE_DIR=$MEDIA_PROJECT_DIR/pipe
export MEDIA_TESTS_DIR=$MEDIA_PROJECT_DIR/tests
