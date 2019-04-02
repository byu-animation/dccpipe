# Will install a virtual environment in the current folder.

pipenv --rm
export PIPENV_VENV_IN_PROJECT=true
pipenv install --dev
