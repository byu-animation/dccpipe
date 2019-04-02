# Deploy the repository (for use in a central location)
pipenv --rm
export PIPENV_VENV_IN_PROJECT=true
pipenv install
