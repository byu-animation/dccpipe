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

# qt-webkit-devel python-devel
dependencies="cmake qt-devel qt5-qtbase-devel libxml2-devel libxslt-devel rpmdevtools gcc gcc-c++ make"

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
fi

# https://askubuntu.com/questions/586938/undo-the-sudo-within-a-script
if [ $(id -u) -ne 0 ]
  then
    pip install --user pyside2
  else
    sudo -u $USER pip install --user pyside2
fi

if [ $(id -u) -ne 0 ]
then
  USERHOME=$HOME
else
  USERHOME=$(eval echo ~${USER})
fi

shopt -s dotglob
cp -r $USERHOME/.local/lib/python2.7/site-packages/*shiboken* $MEDIA_PROJECT_DIR/.venv/lib/python2.7/site-packages
cp -r $USERHOME/.local/lib/python2.7/site-packages/*pyside2* $MEDIA_PROJECT_DIR/.venv/lib/python2.7/site-packages
cp -r $USERHOME/.local/lib/python2.7/site-packages/*PySide2* $MEDIA_PROJECT_DIR/.venv/lib/python2.7/site-packages
