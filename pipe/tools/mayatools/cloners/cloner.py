# TODO: removing the next line to be able to load departments from a config file down the line. Once config is ready, load depts from there.
# from pipe.am.environment import Department
import pipe.gui.select_from_list as sfl
import pipe.gui.quick_dialogs as qd
from pipe.tools.mayatools.utils.utils import *
from pipe.tools.mayatools.publishers.publisher import MayaPublisher as Publisher
from pipe.am.project import Project
from pipe.am.body import Body
from pipe.am.element import Element

from PySide2 import QtWidgets
import maya.cmds as mc
import maya.OpenMayaUI as omu
import os


class MayaCloner:
	def __init__(self):
		self.maya_checkout_dialog = None
		self.quick = False

	def rollback(self):
		print("Rollin' Rollin' Rollin' (Back)")

	def quick_clone(self):
		self.quick = True
		self.go()

	def clone(self, gui=True, file_path=None, asset_name='Temp'):
		if gui:
			self.go()
		else:
			# TODO: make this method work
			self.non_gui_open(file_path, asset_name)

	def non_gui_open(self, filePath=None, assetName='Temp'):
		if filePath == None:
			print 'no file'
			return
		if os.path.exists(filePath):
			mc.file(filePath, open=True, force=True)
			print "open file " + assetName
		else:
			print 'File does not exist: '+assetName

	def go(self):
		project = Project()
		asset_list = project.list_assets()
		self.item_gui = sfl.SelectFromList(l=asset_list, parent=maya_main_window(), title="Select an asset to clone")
		self.item_gui.submitted.connect(self.results)

	def get_element_option(self, type, body):  # FIXME: this would go better in Body()
		element = None

		if type == AssetType.PROP:
			element = body.get_element("model")
			self.department = "model"

		elif type == AssetType.ACTOR:
			response = qd.binary_option("Which department for " + str(body.get_name()) + "?", "model", "rig")
			if response:
				element = body.get_element("model")
				self.department = "model"
			elif response is not None:
				element = body.get_element("rig")
				self.department = "rig"
			else:
				return None

		elif type == AssetType.SET:
			element = body.get_element("model")
			self.department = "model"

		elif type == AssetType.SHOT:
			response = qd.binary_option("Which department for " + str(body.get_name()) + "?", "model", "anim")
			if response:
				element = body.get_element("model")
				self.department = "model"
			elif response is not None:
				element = body.get_element("anim")
				self.department = "anim"
			else:
				return None

		print("element: ", element)

		return element

	def results(self, value):
		print("Final value: ", value[0])
		filename = value[0]

		project = Project()
		body = project.get_body(filename)
		self.body = body
		type = body.get_type()
		element = self.get_element_option(type, body)

		if self.quick:
			latest = element.get_last_publish()
			if not latest:
				qd.error("There have been no publishes in this department.")
				return
			else:
				selected_scene_file = latest[3]
				self.open_scene_file(selected_scene_file)
				return

		if element is None:
			qd.warning("Nothing was cloned.")
			return

		self.publishes = element.list_publishes()
		print("publishes: ", self.publishes)

		if not self.publishes:
			qd.error("There have been no publishes in this department. Maybe you meant model?")
			return

		# make the list a list of strings, not tuples
		self.sanitized_publish_list = []
		for publish in self.publishes:
			path = publish[3]
			file_ext = path.split('.')[-1]
			if not file_ext == "mb":
				continue
			label = publish[0] + " " + publish[1] + " " + publish[2]
			self.sanitized_publish_list.append(label)

		self.item_gui = sfl.SelectFromList(l=self.sanitized_publish_list, parent=maya_main_window(), title="Select publish to clone")
		self.item_gui.submitted.connect(self.publish_selection_results)

	def publish_selection_results(self, value):

		selected_publish = None
		for item in self.sanitized_publish_list:
			if value[0] == item:
				selected_publish = item

		selected_scene_file = None
		for publish in self.publishes:
			label = publish[0] + " " + publish[1] + " " + publish[2]
			if label == selected_publish:
				selected_scene_file = publish[3]

		# selected_scene_file is the one that contains the scene file for the selected commit
		self.open_scene_file(selected_scene_file)

	def open_scene_file(self, selected_scene_file):
		if selected_scene_file is not None:
			check_unsaved_changes()
			setPublishEnvVar(self.body.get_name(), self.department)

			if not os.path.exists(selected_scene_file):
				mc.file(new=True, force=True)
				mc.file(rename=selected_scene_file)
				mc.file(save=True, force=True)
				print "New file: " + selected_scene_file
			else:
				mc.file(selected_scene_file, open=True, force=True)
				print "File opened: " + selected_scene_file

			return True
		else:
			return False
