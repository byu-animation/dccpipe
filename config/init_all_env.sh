SOURCEDIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
source $SOURCEDIR/init_media_env.sh

source $MEDIA_PROJECT_DIR/.venv/bin/activate
source $MEDIA_PROJECT_DIR/init_media_env.sh
source $MEDIA_PROJECT_DIR/init_pyside_env.sh
