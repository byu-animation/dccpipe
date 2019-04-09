#!/bin/sh

original_dir="$(pwd)"
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
cd $SCRIPT_DIR
source ../config/init_all_env.sh
cd $original_dir

echo $PYTHONPATH

echo "here"
dir=`dirname $0`

pwd=$(pwd)

export PYTHONPATH=${PYTHONPATH}:${MEDIA_PIPE_DIR}

echo ${MEDIA_TOOLS_DIR}

cd ${pwd}
