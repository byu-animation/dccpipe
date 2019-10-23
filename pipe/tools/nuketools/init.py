import nuke
import os

# Add subfolders to path to make this a little cleaner
icons_dir = os.environ.get("ICONS_DIR")

nuke.pluginAddPath(icons_dir)
# nuke.pluginAddPath('./scripts')
