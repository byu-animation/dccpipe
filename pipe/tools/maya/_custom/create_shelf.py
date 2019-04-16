#### Shelf code written for the BYU Animation Program by
#### Murphy Randle (murphyspublic@gmail.com). Inspiration and some code
#### snippets taken from http://etoia.free.fr/?p=1771

####
#  /$$   /$$		   /$$ /$$		   /$$ /$$
# | $$  | $$		  | $$| $$		  | $$| $$
# | $$  | $$  /$$$$$$ | $$| $$  /$$$$$$ | $$| $$
# | $$$$$$$$ /$$__  $$| $$| $$ /$$__  $$| $$| $$
# | $$__  $$| $$$$$$$$| $$| $$| $$  \ $$|__/|__/
# | $$  | $$| $$_____/| $$| $$| $$  | $$
# | $$  | $$|  $$$$$$$| $$| $$|  $$$$$$/ /$$ /$$
# |__/  |__/ \_______/|__/|__/ \______/ |__/|__/
####
#### Welcome to the shelf script!
####
#### If you'd like to add a shelf button, you can add it to
#### shelf.json. Follow the example of the other buttons in there.
#### Remember, the icon must be a 33X33 .xpm, and the pythonFile key
#### must be the name of the file where your python script is
#### stored. (Careful, it's not an absolute path!)
####
import pymel.core as pm
import os
import sys
import json
from pipe.am.environment import Environment

environment = Environment()

#### CONSTANTS, Edit these for customization.
PROJ = environment.get_project_name()
# making temp environment name for testing TODO: REMOVE
PROJ = "test_shelf"

SHELF_DIR = os.environ.get('MAYA_SHELF_DIR')
ICON_DIR = os.environ.get('MAYA_ICONS_DIR')
# ICON_DIR = os.path.join(os.environ.get('BYU_TOOLS_DIR'), "assets", "images", "icons", "tool-icons")
# SCRIPT_DIR = os.path.join(SHELF_DIR, "scripts")  # FIXME: currently not doing anything
####

#### Shelf building code. You shouldn't have to edit anything
#### below these lines. If you want to add a new shelf item,
#### follow the instructions in shelf.json.

# FIXME: This line below is deprecated
# sys.path.append(SCRIPT_DIR)

def load_shelf():
	delete_shelf()

	gShelfTopLevel = pm.mel.eval('global string $gShelfTopLevel; string $temp=$gShelfTopLevel')
	pm.shelfLayout(PROJ, cellWidth=33, cellHeight=33, p=gShelfTopLevel)

	#### Okay, for some reason, deleting the shelf from a shelf button crashes Maya.
	#### I'm saving this for another day, or for someone more adventurous.
	#### Make the hard-coded reload button:
	# shelfButton(command="printcow()", annotation="Reload the shelf",
	#			 image=os.path.join(ICON_DIR, "reload.xpm"))

	#### Load in the buttons
	json_file = file(os.path.join(SHELF_DIR, "shelf.json"))
	data = json.loads(json_file.read())
	for shelf_item in data['shelf_items']:
		if shelf_item['itemType'] == 'button':
			icon = os.path.join(ICON_DIR, shelf_item['icon'])
			annotation = shelf_item['annotation']
			module = "pipe." + shelf_item['guiTool']
			function = shelf_item['function'] + "()"
			pm.shelfButton(command="import %s; %s"%(module, function),annotation=annotation, image=icon, label=annotation)
		else:
			pm.separator(horizontal='0', style='shelf', enable='1', width=35, height=35, visible=1, backgroundColor=(0.5,0.5,0.5), highlightColor=(0.321569, 0.521569, 0.65098))
			# pm.separator(horizontal=False, style='none', enable=True, width=7)
			# pm.separator(horizontal=False, style='shelf', enable=True, width=2, backgroundColor=(0.5,0.5,0.5))
			# pm.separator(horizontal=False, style='none', enable=True, width=7)


	#setUpSoup(gShelfTopLevel)
	# Set default preferences
	pm.env.optionVars['generateUVTilePreviewsOnSceneLoad'] = 1

def delete_shelf():
	if pm.shelfLayout(PROJ, exists=True):
		pm.deleteUI(PROJ)
