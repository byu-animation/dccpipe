#!/bin/sh

for arg in "$@"
do
    if [ "$arg" == "--help" ] || [ "$arg" == "-h" ]
    then
cat << EOF

Fedora Install Script

Usage:
install.sh -d | --dev
install.sh -c | --clean
install.sh -im | --installmissing
install.sh -h | --help

Options:
-d --dev              Install developer packages
-c --clean            Clear virtualenv and reinstall
-im --installmissing  Install missing pip/yum packages
-h --help             Help and usage

EOF
  return 1
  fi
  if [ "$arg" == "--dev" ] || [ "$arg" == "-d" ]
  then
    DEV=1
  fi
  if [ "$arg" == "--clean" ] || [ "$arg" == "-c" ]
  then
    CLEAN=1
  fi
  if [ "$arg" == "--installmissing" ] || [ "$arg" == "-im" ]
  then
    INSTALLMISSINGPACKAGES=1
  fi
done

if [ $MEDIA_SUBSHELL_ACTIVE ] && [ "$MEDIA_SUBSHELL_ACTIVE" -eq "1" ]
then
  deactivate
  export MEDIA_SUBSHELL_ACTIVE="0"
fi

FEDORADIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
CONFIGDIR=$FEDORADIR
while [ "$(basename $CONFIGDIR)" != "/" ] && [ "$(basename $CONFIGDIR)" != "config" ]
do
  CONFIGDIR="$(dirname "$CONFIGDIR")"
done
source $CONFIGDIR/unix/env.sh

original_dir=$(pwd)
cd $MEDIA_PROJECT_DIR

if [ $CLEAN ] && [ $CLEAN -eq 1 ]
  then
  rm -rf $MEDIA_PROJECT_DIR/.venv
fi


function isinstalled {
  if [ "$(pip list | grep "$@" 2>/dev/null)" ] || yum list installed "$@" >/dev/null 2>&1; then
    true
  else
    false
  fi
}

dependencies="pip pipenv"
FAILED=0
for dependency in ${dependencies} ; do
  echo "checking if" $dependency "is installed"
  if isinstalled $dependency
  then
    echo "requirement satisfied:" $dependency

  elif [ $INSTALLMISSINGPACKAGES -eq 1 ]
  then
    echo "installing " $dependency
    PIPFAILED=0
    YUMFAILED=0
    if [ "$(id -u)" -ne "0" ]
      then
        if pip install --user $dependency >/dev/null 2>&1
        then
          echo "pip install succeeded"
          continue
        else
          echo "pip install failed"
          PIPFAILED=1
        fi
      else
        if sudo -u $USER pip install --user $dependency >/dev/null 2>&1
        then
          echo "pip install succeeded"
          continue
        else
          echo "pip install failed"
          PIPFAILED=1
        fi
    fi
    if yum install $dependency >/dev/null 2>&1
    then
      echo "yum install succeeded"
      continue
    else
      echo "yum install failed"
      YUMFAILED=1
    fi
    if [ $PIPFAILED -eq 1 ] && [ $YUMFAILED -eq 1 ]
      then
        FAILED=1
        continue
    fi

  else
    echo $dependency "not installed. Please install as root."
    FAILED=1
    continue
  fi
done

if [ $FAILED ] && [ $FAILED -eq 1 ]
  then
    echo "Build failed. Check your dependencies, and install with sudo if you can."
    return 1
fi

# https://askubuntu.com/questions/586938/undo-the-sudo-within-a-script

source $CONFIGDIR/unix/env.sh

# Install a virtual environment in the current folder.
export PIPENV_VENV_IN_PROJECT=true

# Install dev tools if dev is true
if [ $DEV ] && [ $DEV -eq 1 ]
then
    echo "got to pipenv install"
    pipenv install --dev
else
    pipenv install
fi

if [ $INSTALLMISSINGPACKAGES ] && [ $INSTALLMISSINGPACKAGES -eq 1 ]
then
  source $FEDORADIR/install_pyside.sh --installmissing
else
  source $FEDORADIR/install_pyside.sh
fi

if [ $(id -u) -eq 0 ]
then
  echo "Install was run as root. Changing permissions in directory:" $MEDIA_PROJECT_DIR/.venv
  sudo chmod 777 .
  sudo chmod -R 777 $MEDIA_PROJECT_DIR/.venv
fi

cd $original_dir
