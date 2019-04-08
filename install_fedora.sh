#!/bin/bash
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
        rm -rf .pyenv
    fi
    if [ "$arg" == "--installmissing"] || [ "$arg" == "-im"]
    then
        INSTALLMISSINGPACKAGES=1
    else
        INSTALLMISSINGPACKAGES=0
    fi
done

MEDIA_PROJECT_DIR=$(pwd)

if [ ! -d .pyenv ]
    then
    mkdir .pyenv
    git clone https://github.com/pyenv/pyenv.git .pyenv
fi

source init_pyenv.sh 3.7.3
pyenv install 3.7.3
pyenv install 2.7.15
source init_pyenv.sh 3.7.3

pip install pipenv --user

# Install a virtual environment in the current folder.
export PIPENV_VENV_IN_PROJECT=true

# Install dev tools if dev is true
if [ DEV == 1 ]
then
    pipenv install --dev
else
    pipenv install
fi

if [ INSTALLMISSINGPACKAGES == 1 ]
then
  source build_pyside_fedora.sh --installmissing
else
  source build_pyside_fedora.sh
fi
