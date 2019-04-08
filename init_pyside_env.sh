#!/bin/sh

source init_media_env.sh

if [ ! -d .pyside ]
    then
    mkdir $MEDIA_PROJECT_DIR/.pyside
fi

export PYSIDEPATH=$MEDIA_PROJECT_DIR/.pyside
export PATH=$PYSIDEPATH/bin:$PATH
export PYTHONPATH=$PYSIDEPATH/lib/python2.6/site-packages:$PYSIDEPATH
export LD_LIBRARY_PATH=$PYSIDEPATH/lib:$PYSIDEPATH
export PKG_CONFIG_PATH=$PYSIDEPATH/lib/pkgconfig:$PYSIDEPATH
