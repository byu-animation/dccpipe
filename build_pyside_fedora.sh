# https://wiki.qt.io/Building_PySide_on_Linux
# This whole script is adapted from the PySide build guide

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
  if yum list installed "$@" >/dev/null 2>&1; then
    true
  else
    false
  fi
}

dependencies = ("cmake" "qt-devel" "qt-webkit-devel" "libxml2-devel" "libxslt-devel" "python-devel" "rpmdevtools" "gcc" "gcc-c++" "make")

for dependency in ${dependencies} ; do
  if [ ! isinstalled $dependency && INSTALLMISSINGPACKAGES ]
    then
      yum install $dependency --installroot=$PYSIDEPATH/bin
    else
      echo $dependency "not installed. Please install as root."
  fi
done

source init_pyside_env.sh

# set -DENABLE_ICECC=1 if you're using the icecream distributed compiler
alias runcmake='cmake .. -DCMAKE_INSTALL_PREFIX=$PYSIDEPATH -DCMAKE_BUILD_TYPE=Debug -DENABLE_ICECC=0'

#!/usr/bin/env bash

allrepos="apiextractor generatorrunner shiboken pyside pyside-mobility"

for repo in ${allrepos} ; do
 git clone git://gitorious.org/pyside/$repo.git
done

#!/usr/bin/env bash

alldirs=("apiextractor" "generatorrunner" "shiboken" "pyside" "pyside-mobility")

if [ $# == 0 ] ; then
 dirs=("${alldirs[@]}")
else
 dirs=("$@")
fi

for d in "${dirs[@]}" ; do
 (cd "$d"
 git pull origin master
 ) # exit from "$d"
done

#!/usr/bin/env bash

alldirs=("apiextractor" "generatorrunner" "shiboken" "pyside")

if [ $# == 0 ] ; then
 dirs=("${alldirs[@]}")
else
 dirs=("$@")
fi

for d in "${dirs[@]}" ; do
 rm -rf "$d/build"
 mkdir -p "$d/build"
 (cd "$d/build"
 runcmake .. && make -j4 && make install || exit 1
 ) # exit from "$d/build"
done
