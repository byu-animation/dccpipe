'''
	Welcome to the Maya shelf script!

	If you'd like to add a shelf button, you can add it to
	shelf.json. Follow the example of the other buttons in there.
	Remember, the icon should be a .svg and the function
	must be implemented in the specified tool location
'''
import pymel.core as pm
import os
import sys
import json
from pipe.am.environment import Environment
from pipe.tools.mayatools.utils.reload_scripts import *


environment = Environment()
PROJ = environment.get_project_name()
SHELF_DIR = os.environ.get('MAYA_SHELF_DIR')
ICON_DIR = os.environ.get('MAYA_ICONS_DIR')
os.environ["DCC_ASSET_NAME"] = ""
os.environ["DCC_DEPARTMENT"] = ""

'''
	Shelf building code. You shouldn't have to edit anything
	below these lines. If you want to add a new shelf item,
	follow the instructions at the top of this file.
'''
def load_shelf():
	delete_shelf()
	ReloadScripts().go()

	gShelfTopLevel = pm.mel.eval('global string $gShelfTopLevel; string $temp=$gShelfTopLevel')
	pm.shelfLayout(PROJ, cellWidth=33, cellHeight=33, p=gShelfTopLevel)

	# Load in the buttons
	json_file = file(os.path.join(SHELF_DIR, "shelf.json"))
	data = json.loads(json_file.read())
	for shelf_item in data['shelfItems']:
		if shelf_item['itemType'] == 'button':
			icon = os.path.join(ICON_DIR, shelf_item['icon'])
			annotation = shelf_item['annotation']
			label = shelf_item['label']

			path = "pipe.tools." + shelf_item['tool']
			function = shelf_item['function']
			class_with_method = function.split(".")
			module = class_with_method[0]
			method = class_with_method[1]

			command = "from " + str(path) + " import " + str(module) + "; shelf_item = " + str(module) + "(); shelf_item." + str(method)

			pm.shelfButton(command=command, annotation=annotation, image=icon, l=annotation, iol=label, olb=(0,0,0,0))
		else:
			pm.separator(horizontal=False, style='shelf', enable=True, width=35, height=35, visible=1, enableBackground=0, backgroundColor=(0.2,0.2,0.2), highlightColor=(0.321569, 0.521569, 0.65098))

	# Set default preferences
	pm.env.optionVars['generateUVTilePreviewsOnSceneLoad'] = 1

	# shelf loaded correctly
	print("*** Shelf loaded :) ***")
	sys.path.append(os.getcwd())

def delete_shelf():
	if pm.shelfLayout(PROJ, exists=True):
		pm.deleteUI(PROJ)
