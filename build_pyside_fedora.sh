# This script is adapted from the PySide build guide:
# https://wiki.qt.io/Building_PySide_on_Linux

for arg in "$@"
do
    if [ "$arg" == "--installmissing" ] || [ "$arg" == "-im" ]
    then
        INSTALLMISSINGPACKAGES=1
    else
        INSTALLMISSINGPACKAGES=0
    fi
done

#https://unix.stackexchange.com/questions/122681/how-can-i-tell-whether-a-package-is-installed-via-yum-in-a-bash-script

function isinstalled {
  if rpm -q "$1" >/dev/null 2>&1; then
    true
  else
    false
  fi
}

dependencies="cmake qt-devel qt5-qtbase-devel qt-webkit-devel libxml2-devel libxslt-devel python-devel rpmdevtools gcc gcc-c++ make"

FAILED=0
for dependency in ${dependencies} ; do
  echo "checking if" $dependency "is installed"
  if isinstalled $dependency
    then
      echo "requirement satisfied:" $dependency
    elif [ $INSTALLMISSINGPACKAGES == 1 ]
    then
      echo "installing " $dependency
      TMP=$(mktemp)
      yum install $dependency 2> "$TMP"
      err=$(cat "$TMP")
      rm "$TMP"
      if [ ! -z "$err" ]
      then
        echo "install failed"
        #echo $err
        FAILED=1
      else
        echo "install succeeded"
      fi
    else
      echo $dependency "not installed. Please install as root."
      FAILED=1
  fi
done

if [ $FAILED == 1 ]
  then
    echo "Build failed. Check your dependencies, and install with sudo if you can."
    exit 1
fi

source ./init_pyside_env.sh
cd $PYSIDEPATH

# set -DENABLE_ICECC=1 if you're using the icecream distributed compiler
alias runcmake='cmake .. -DCMAKE_INSTALL_PREFIX=$PYSIDEPATH -DCMAKE_BUILD_TYPE=Debug -DENABLE_ICECC=0'

#!/usr/bin/env bash

allrepos="apiextractor generatorrunner shiboken pyside pyside-mobility"

for repo in ${allrepos} ; do
 git clone git://github.com/pyside/$repo.git
done

#!/usr/bin/env bash

dirs="apiextractor generatorrunner shiboken pyside pyside-mobility"

for d in ${dirs} ; do
 (cd "$d"
 git pull origin master
 ) # exit from "$d"
done

for d in ${dirs} ; do
 rm -rf "$d/build"
 mkdir -p "$d/build"
 (cd "$d/build"
  cmake .. -DCMAKE_INSTALL_PREFIX=$PYSIDEPATH -DCMAKE_BUILD_TYPE=Debug -DENABLE_ICECC=0 && make -j4 && make install || exit 1
 ) # exit from "$d/build"
done
