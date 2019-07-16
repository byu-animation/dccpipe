from pipe.gui.select_from_list import SelectFromList as sfl
from pipe.tools.mayatools.utils.utils import *
from pipe.gui.quick_dialogs import message as message_gui
from pipe.am.environment import Department
from pipe.am import pipeline_io
import pymel.core as pm
from PySide2 import QtWidgets
import maya.OpenMayaUI as omu
import os
import time


class MayaReferencer:

	def __init__(self):
		pass

	def post_reference(self, dialog, useNamespace=False):
		file_paths = dialog.filePaths
		done = dialog.done
		isReferenced = dialog.reference

		print "The filePaths are", file_paths
		print "The reference is", isReferenced
		if dialog.getDepartment() in Department.CROWD_DEPTS:
			referenceCrowdCycle(file_paths)
		else:
			reference(file_paths, isReferenced=isReferenced, useNamespace=useNamespace)

	def reference(self, filePaths, isReferenced=True, useNamespace=False):
		if filePaths is not None and isReferenced:
			empty = []
			for path in filePaths:
				print "This is the path that we are working with", path
				if os.path.exists(path):
					print path, "exists"
					#TODO do we want to add multiple references in with different namespaces? You know to get rid of conflicts? Or is our current system for handling that good enough?
					# pm.system.createReference(path, namespace="HelloWorld1")
					basename = os.path.basename(path)
					millis = pipeline_io.timestamp()
					refNamespace = basename + str(millis)
					print basename
					print str(millis)
					print refNamespace
					if useNamespace:
						pm.system.createReference(path, namespace=refNamespace)
					else:
						pm.system.createReference(path)
				else:
					print path, "don't exist"
					empty.append(path)

			if empty:
				empty_str = '\n'.join(empty)
				error_dialog = QtWidgets.QErrorMessage(maya_main_window())
				error_dialog.showMessage("The following elements are empty. Nothing has been published to them, so they can't be referenced.\n"+empty_str)
		# if not done:
		#	 go()

	def referenceCrowdCycle(self, paths):
		pm.loadPlugin('AbcImport')
		for cycle in paths:
			if not os.path.exists(cycle):
				print 'this is the type', type(cycle)
				print 'The cycle doesn\'t exist. That seems weird.', cycle
				print os.path.exists(str(cycle)), 'this is another shot'
				return
			fileName = os.path.basename(cycle)
			#The file is going to be an alembic so we can drop the last four characters '.abc' to get the file name
			cycleName = fileName[:len(fileName)-4]

			invalidInput = True
			while(invalidInput):
				try:
					refCount = int(message_gui.input('How many times do you want to reference this cycle?'))
				except ValueError:
					message_gui.error('Please enter a number')
					continue
				invalidInput = False

			for i in range(refCount):
				time.sleep(1) # sleep for a bit to make sure out namespace is unique
				millis = pipeline_io.timestamp()
				namespace = cycleName + str(millis)

				cycleRefGroup = namespace + 'RNgroup'
				cycleControls = namespace + '_controls'
				offset = 'offset'
				speed = 'speed'
				cycleType = 'cycleType'
				translate = 'translate'
				rotate = 'rotate'
				scale = 'scale'
				refAlembicNode = namespace + ':' + cycleName + '_AlembicNode'
				refAlembicOffset = refAlembicNode + '.' + offset
				refAlembicSpeed = refAlembicNode + '.' + speed
				refAlembicCycleType = refAlembicNode + '.' + cycleType
				controlAlembicOffset = cycleControls + '.' + offset
				controlAlembicSpeed = cycleControls + '.' + speed

				cycleRefTranslate = cycleRefGroup + '.' + translate
				cycleRefScale = cycleRefGroup + '.' + scale
				cycleRefRotate = cycleRefGroup + '.' + rotate

				controlAlembicTranslate = cycleControls + '.' + translate
				controlAlembicScale = cycleControls + '.' + scale
				controlAlembicRotate = cycleControls + '.' + rotate

				pm.system.createReference(cycle, groupReference=True, namespace=namespace)

				node = pm.ls(cycleRefGroup)[0]
				circ = pm.circle(r=0.25,nr=(0, 1, 0), n=cycleControls)[0]
				parentGroupName = namespace + 'agent'
				group = pm.group(name=parentGroupName, em=True)

				pm.parent(circ, group)
				pm.parent(node, group)

				if circ.hasAttr(offset):
					circ.deleteAttr(offset)
				if circ.hasAttr(speed):
					circ.deleteAttr(speed)
				circ.addAttr(offset, at='double', hidden=False, dv=0.0, k=True)
				circ.addAttr(speed, at='double', hidden=False, dv=1.0, k=True)

				# Add agent tag so the exporter can easily find it
				crowdAgentFlag = 'BYU_Crowd_Agent_Flag'
				if group.hasAttr(crowdAgentFlag):
					group.deleteAttr(crowdAgentFlag)
				group.addAttr(crowdAgentFlag, at=bool, hidden=False, dv=True, k=True)


				# When passing in arguments to connectAttr remember that attr 1 controls attr 2
				pm.connectAttr(controlAlembicOffset, refAlembicOffset)
				pm.connectAttr(controlAlembicSpeed, refAlembicSpeed)
				pm.setAttr(refAlembicCycleType, 1)
				pm.connectAttr(controlAlembicTranslate, cycleRefTranslate)
				pm.connectAttr(controlAlembicRotate, cycleRefRotate)
				pm.connectAttr(controlAlembicScale, cycleRefScale)

	def results(self, values):

		print("values: ", values)
		# def createReference(self):
		selected = []
		# del self.filePaths[:]
		for item in self.assetList.selectedItems():
			body = self.project.get_body(str(item.text()))
			element = body.get_element(str(self.departmentMenu.currentText()))
			if self.getDepartment() in Department.CROWD_DEPTS:
				cacheDir = element.get_cache_dir()
				for filePath in os.listdir(cacheDir):
					self.filePaths.append(os.path.join(cacheDir, filePath))
			else:
				path = element.get_app_filepath()
				self.filePaths.append(path)
			selected.append(str(item.text()))
		checkout = self.project.get_checkout(os.path.dirname(self.src))
		if checkout is not None:
			body_name = checkout.get_body_name()
			body = self.project.get_body(body_name)
			for sel in selected:
				body.add_reference(sel)
		self.done = False
		self.reference = True
		self.close()


	def go(self, useNamespace=True):
		self.filePath = pm.system.sceneName()
		self.maya_reference_dialog = sfl(l=[Department.MODEL, Department.RIG, Department.CYCLES], parent=maya_main_window(), title="Select references", multiple_selection=True)
		self.maya_reference_dialog.submitted.connect(self.results)
