#!/bin/sh

# https://askubuntu.com/questions/586938/undo-the-sudo-within-a-script
if [ "$(id -u)" -ne "0" ]
  then
    pip install --user pyside2
  else
    sudo -u $USER pip install --user pyside2
fi

if [ "$(id -u)" -ne "0" ]
  then
    USERHOME=$HOME
  else
    USERHOME=$(eval echo ~${USER})
fi

shopt -s dotglob
cp -r $USERHOME/Library/Python/2.7/lib/python/site-packages/*shiboken* $MEDIA_PROJECT_DIR/.venv/lib/python2.7/site-packages
cp -r $USERHOME/Library/Python/2.7/lib/python/site-packages/*pyside2* $MEDIA_PROJECT_DIR/.venv/lib/python2.7/site-packages
cp -r $USERHOME/Library/Python/2.7/lib/python/site-packages/*PySide2* $MEDIA_PROJECT_DIR/.venv/lib/python2.7/site-packages
