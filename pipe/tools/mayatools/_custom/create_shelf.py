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

			# dcc = double click command: we can add a different command that goes when double clicked.
			dcc = shelf_item['double-click']
			# menu = submenu for right-click
			menu = shelf_item['menu']

			path = "pipe.tools." + shelf_item['tool']
			function = shelf_item['function']
			class_with_method = function.split(".")
			module = class_with_method[0]
			method = class_with_method[1]

			command_base = "from " + str(path) + " import " + str(module) + "; shelf_item = " + str(module) + "(); shelf_item."
			command = command_base + str(method)

			if dcc == 0:
				dcc = command
			else:
				dcc = command_base + str(dcc)

			if menu == 0:
				pm.shelfButton(c=command, ann=annotation, i=icon, l=annotation, iol=label, olb=(0,0,0,0), dcc=dcc)
			elif menu == 1:
				menu_items = shelf_item['menu_items']
				new_menu = build_menu_string(command_base, menu_items)
				mip = []
				for i in range (len(new_menu)):
					mip.append(i)
				pm.shelfButton(c=command, ann=annotation, i=icon, l=annotation, iol=label, olb=(0,0,0,0), dcc=dcc, mi=new_menu, mip=mip)

		else:
			pm.separator(horizontal=False, style='shelf', enable=True, width=35, height=35, visible=1, enableBackground=0, backgroundColor=(0.2,0.2,0.2), highlightColor=(0.321569, 0.521569, 0.65098))

	project_tools = get_production_scripts()
	if project_tools:
		pm.separator(horizontal=False, style='shelf', enable=True, width=35, height=35, visible=1, enableBackground=0, backgroundColor=(0.2,0.2,0.2), highlightColor=(0.321569, 0.521569, 0.65098))

		custom_modules = []
		for tool in project_tools:
			module = tool['function'].split(".")[0]
			custom_modules.append(module)

		create_tools_init(custom_modules)

		for tool in project_tools:
			name = tool['name']
			description = tool['description']
			icon = os.path.join(Environment().get_tools_dir(), tool['icon'])
			label = tool['label']
			function = tool['function']

			pm.shelfButton(c=get_production_tool_command(function), ann=description, i=icon, l=name, iol=label, olb=(0,0,0,0), dcc=dcc)

	# Set default preferences
	pm.env.optionVars['generateUVTilePreviewsOnSceneLoad'] = 1

	# shelf loaded correctly
	print("*** Shelf loaded :) ***")
	sys.path.append(os.getcwd())

def build_menu_string(command_base, menu_items):
	menu = []
	menu_python = [0,1,2,3]
	for item in menu_items.items():
		menu_command = command_base + str(item[1])
		label = item[0]
		new_item = [label, menu_command]
		menu.append(new_item)

	return menu

def delete_shelf():
	if pm.shelfLayout(PROJ, exists=True):
		pm.deleteUI(PROJ)

def get_production_scripts():
	create_production_init()
	scripts_dir = Environment().get_tools_dir()
	scripts_json = os.path.join(scripts_dir, "maya_scripts.json")
	json_file = file(scripts_json)
	data = json.loads(json_file.read())

	return data["scripts"]

def get_production_tool_command(function):
	module = function.split(".")[0]
	command = "try:\n  from production.tools import " + str(module) + "; " + function
	command += "\nexcept Exception as e:\n  print(str(e))"

	return command

def create_tools_init(modules):
	tools_dir = Environment().get_tools_dir()

	init_file = open(tools_dir + "/__init__.py", "w")
	init_file.write("__all__ = " + str(modules))

def create_production_init():
	production_dir = Environment().get_production_dir()

	init_file = open(production_dir + "/__init__.py", "w")
	init_file.write("__all__ = ['tools']")
