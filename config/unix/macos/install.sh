#!/bin/sh

for arg in "$@"
do
    if [ "$arg" == "--help" ] || [ "$arg" == "-h" ]
    then
cat << EOF

macOS Install Script

Usage:
install.sh -d | --dev
install.sh -c | --clean
install.sh -im | --installmissing
install.sh -h | --help

Options:
-d --dev              Install developer packages
-c --clean            Clear virtualenv and reinstall
-im --installmissing  Install missing pip/brew packages
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

# brew is required for macOS config
echo "Checking if brew installed..."
if brew >/dev/null 2>&1; then
  echo "brew is not installed, aborting"
  return 1
else
  echo "brew is installed!"
fi

if [ $MEDIA_SUBSHELL_ACTIVE ] && [ "$MEDIA_SUBSHELL_ACTIVE" -eq "1" ]
then
  deactivate
  export MEDIA_SUBSHELL_ACTIVE="0"
fi

MACOSDIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
CONFIGDIR=$MACOSDIR
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
  if pip list | grep "$@" 2>/dev/null || brew list "$@"; then
    echo "$@ is installed"
    true
  else
    echo "$@ is not installed"
    false
  fi
}

# Install python through brew
isinstalled python@2
installed=$?
if ! $(exit $installed)
then
  echo "installing python 2.7 through brew"
  brew install python@2
  isinstalled python@2
  installed=$?
  if ! $(exit $installed)
  then
    echo "python 2.7 install failed"
    return 1
  fi
fi

# Install pipenv through pip
isinstalled pipenv
installed=$?
if ! $(exit installed)
then
  echo "installing pipenv through pip"
  pip install pipenv
  isinstalled pipenv
  installed=$?
  if ! $(exit $installed)
  then
    echo "pipenv install failed"
    return 1
  fi
fi

# https://askubuntu.com/questions/586938/undo-the-sudo-within-a-script
source $CONFIGDIR/unix/env.sh

# Install a virtual environment in the current folder.
export PIPENV_VENV_IN_PROJECT=true

# Install dev tools if dev is true
# make sure the PATH is correct
export PATH=~/.local/bin:$PATH

if [ $DEV ] && [ $DEV -eq 1 ]
then
    echo "got to pipenv install"
    pipenv install --dev
else
    pipenv install
fi

if [ $INSTALLMISSINGPACKAGES ] && [ $INSTALLMISSINGPACKAGES -eq 1 ]
then
  source $MACOSDIR/install_pyside.sh --installmissing
else
  source $MACOSDIR/install_pyside.sh
fi

if [ $(id -u) -eq 0 ]
then
  echo "Install was run as root. Changing permissions in directory:" $MEDIA_PROJECT_DIR/.venv
  sudo chmod 777 .
  sudo chmod -R 777 $MEDIA_PROJECT_DIR/.venv
fi

cd $original_dir
