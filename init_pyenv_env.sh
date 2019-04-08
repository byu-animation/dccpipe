#!/bin/sh

source init_media_env.sh

export PYENV_VERSION=${1-"2.7.15"}

export PYENV_ROOT="$MEDIA_PROJECT_DIR/.pyenv"
export PATH="$PYENV_ROOT/bin:$PATH"
if [ command -v pyenv 1>/dev/null 2>&1 ]
then
  eval "$(pyenv init -)"
fi
