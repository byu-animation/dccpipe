#!/bin/sh

pipenv shell

echo "here"
dir=`dirname $0`

pwd=$(pwd)

#Get the location of project_env.sh so we can set the environment variables accordingly.
scriptLocation="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd ${scriptLocation}
projectDir="$( cd ../ && pwd )"

#If the specified project directory is not a directory then quit.
if [ ! -d ${projectDir} ] ;
then
	echo ${projectDir}" is not a directory."
	echo "Usage: sh test.sh -p directory/path"
	exit 1
fi

export MEDIA_PROJECT_DIR=${projectDir}
export MEDIA_TOOLS_DIR=${projectDir}/pipe

export PYTHONPATH=${PYTHONPATH}:${MEDIA_TOOLS_DIR}

echo ${MEDIA_TOOLS_DIR}

cd ${pwd}
