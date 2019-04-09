SOURCEDIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
source $SOURCEDIR/init_media_env.sh

export PYSIDEPATH=$MEDIA_PROJECT_DIR/.pyside
export PATH=$PYSIDEPATH/bin:$PATH
export PYTHONPATH=$PYSIDEPATH/lib/python2.6/site-packages:$PYTHONPATH
export LD_LIBRARY_PATH=$PYSIDEPATH/lib:$LD_LIBRARY_PATH
export PKG_CONFIG_PATH=$PYSIDEPATH/lib/pkgconfig:$PKG_CONFIG_PATH
