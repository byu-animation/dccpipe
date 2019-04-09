SOURCEDIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
source $SOURCEDIR/init_media_env.sh

original_dir=$(pwd)
cd $MEDIA_PROJECT_DIR

for arg in "$@"
do
    if [ "$arg" == "--dev" ] || [ "$arg" == "-d" ]
    then
        DEV=1
    else
        DEV=0
    fi
    if [ "$arg" == "--clean" ] || [ "$arg" == "-c" ]
    then
        rm -rf $MEDIA_PROJECT_DIR/.venv
    fi
    if [ "$arg" == "--installmissing" ] || [ "$arg" == "-im" ]
    then
        INSTALLMISSINGPACKAGES=1
    else
        INSTALLMISSINGPACKAGES=0
    fi
done

function isinstalled {
  if [ ! "$(pip list | grep "$@")" ] || yum list installed "$@" >/dev/null 2>&1; then
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
  elif [ $INSTALLMISSINGPACKAGES == 1 ]
  then
    echo "installing " $dependency
    PIPFAILED=0
    YUMFAILED=0
    if [ $(id -u) -ne 0 ]
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
    if [ $PIPFAILED == 1 ] && [ $YUMFAILED == 1 ]
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

if [ $FAILED == 1 ]
  then
    echo "Build failed. Check your dependencies, and install with sudo if you can."
    exit 1
fi

# https://askubuntu.com/questions/586938/undo-the-sudo-within-a-script

source $SOURCEDIR/init_media_env.sh

# Install a virtual environment in the current folder.
export PIPENV_VENV_IN_PROJECT=true

# Install dev tools if dev is true
if [ DEV == 1 ]
then
    pipenv install --dev
else
    pipenv install
fi

if [ $INSTALLMISSINGPACKAGES == 1 ]
then
  source $SOURCEDIR/build_pyside_fedora.sh --installmissing
else
  source $SOURCEDIR/build_pyside_fedora.sh
fi

if [ "$(id -u)" == "0" ]
then
  echo "Install was run as root. Changing permissions in directory:" $MEDIA_PROJECT_DIR/.venv
  sudo chmod 777 .
  sudo chmod -R 777 $MEDIA_PROJECT_DIR/.venv
fi

cd $original_dir
