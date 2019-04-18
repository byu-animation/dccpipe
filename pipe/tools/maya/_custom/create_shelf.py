#### Shelf code written for the BYU Animation Program by
#### Murphy Randle (murphyspublic@gmail.com). Inspiration and some code
#### snippets taken from http://etoia.free.fr/?p=1771

#### Welcome to the shelf script!
####
#### If you'd like to add a shelf button, you can add it to
#### shelf.json. Follow the example of the other buttons in there.
#### Remember, the icon must be a 33X33 .xpm, and the function
#### must be implemented in the specified guiTool location
####
import pymel.core as pm
import os
import sys
import json

# print("before import Environment")
# from pipe.am.environment import Environment

print("imports successful")

# FIXME: I've commented out all references to Environment (importing, calling, etc) until it is working properly
# environment = Environment()

#### CONSTANTS, Edit these for customization.
# PROJ = environment.get_project_name()

# making temp environment name for testing TODO: REMOVE
PROJ = "test_shelf"

SHELF_DIR = os.environ.get('MAYA_SHELF_DIR')
ICON_DIR = os.environ.get('MAYA_ICONS_DIR')
# ICON_DIR = os.path.join(os.environ.get('BYU_TOOLS_DIR'), "assets", "images", "icons", "tool-icons")
####

#### Shelf building code. You shouldn't have to edit anything
#### below these lines. If you want to add a new shelf item,
#### follow the instructions at the top of this file.

def load_shelf():
	delete_shelf()

	gShelfTopLevel = pm.mel.eval('global string $gShelfTopLevel; string $temp=$gShelfTopLevel')
	pm.shelfLayout(PROJ, cellWidth=33, cellHeight=33, p=gShelfTopLevel)

	#### Okay, for some reason, deleting the shelf from a shelf button crashes Maya.
	#### Make the hard-coded reload button:
	# shelfButton(command="printcow()", annotation="Reload the shelf",
	#			 image=os.path.join(ICON_DIR, "reload.xpm"))

	#### Load in the buttons
	json_file = file(os.path.join(SHELF_DIR, "shelf.json"))
	data = json.loads(json_file.read())
	for shelf_item in data['shelfItems']:
		if shelf_item['itemType'] == 'button':
			icon = os.path.join(ICON_DIR, shelf_item['icon'])
			annotation = shelf_item['annotation']
			module = "pipe.tools." + shelf_item['guiTool']
			function = shelf_item['function'] + "()"
			pm.shelfButton(command="import %s; %s"%(module, function),annotation=annotation, image=icon, label=annotation)
			# pm.shelfButton(command="%s.%s"%(module, function),annotation=annotation, image=icon, label=annotation)
		else:
			pm.separator(horizontal=False, style='shelf', enable=True, width=35, height=35, visible=1, enableBackground=0, backgroundColor=(0.2,0.2,0.2), highlightColor=(0.321569, 0.521569, 0.65098))

	# Set default preferences
	pm.env.optionVars['generateUVTilePreviewsOnSceneLoad'] = 1

	print("*** Shelf loaded :) ***")
	print(os.getcwd())
	print(sys.path)
	sys.path.append(os.getcwd())
	print(sys.path)
	# FIXME: getting this error: # Error: ImportError: file <maya console> line 1: No module named Manager # When clicking create_body() icon

def delete_shelf():
	if pm.shelfLayout(PROJ, exists=True):
		pm.deleteUI(PROJ)
