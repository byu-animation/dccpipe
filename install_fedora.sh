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
        rm -rf .venv
        rm -rf .pyside
    fi
    if [ "$arg" == "--installmissing" ] || [ "$arg" == "-im" ]
    then
        INSTALLMISSINGPACKAGES=1
    else
        INSTALLMISSINGPACKAGES=0
    fi
done

function isinstalled {
  if yum list installed "$@" >/dev/null 2>&1; then
    true
  else
    false
  fi
}

dependencies="pipenv"
FAILED=0
for dependency in ${dependencies} ; do
  echo "checking if" $dependency "is installed"
  if isinstalled $dependency
    then
      echo "requirement satisfied:" $dependency
    elif [ $INSTALLMISSINGPACKAGES == 1 ]
    then
      echo "installing " $dependency
      if yum install $dependency --installroot=$PYSIDEPATH/bin >/dev/null 2>&1; then
        echo "install failed"
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

# https://askubuntu.com/questions/586938/undo-the-sudo-within-a-script
sudo -u $USER pip install --user pipenv

source ./init_media_env.sh

if [ INSTALLMISSINGPACKAGES == 1 ]
then
  source ./build_pyside_fedora.sh --installmissing
else
  source ./build_pyside_fedora.sh
fi

# Install a virtual environment in the current folder.
export PIPENV_VENV_IN_PROJECT=true

# Install dev tools if dev is true
if [ DEV == 1 ]
then
    pipenv install --dev
else
    pipenv install
fi
