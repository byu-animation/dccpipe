#!/bin/sh
SOURCEDIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
source $SOURCEDIR/env.sh
export CURRENT_PROGRAM="sbs"

export SUBSTANCE_PLUGINS_DIR=${MEDIA_PROJECT_DIR}'/pipe/tools/sbstools/_custom/'
export SUBSTANCE_ICONS_DIR=${MEDIA_PROJECT_DIR}'/pipe/tools/_resources/'
export PYTHONPATH=${PYTHONPATH}:${MEDIA_PROJECT_DIR}

cp -ar ${MEDIA_PROJECT_DIR}'/pipe/tools/sbstools' ~/Documents/Allegorithmic/Substance\ Painter/plugins/

# Write asset list to an XML file in production
echo "Creating assets.xml"
python ${MEDIA_PROJECT_DIR}'/pipe/tools/sbstools/create_asset_xml.py'

echo "Starting Substance..."
substancepainter ${MEDIA_PROJECT_DIR}
