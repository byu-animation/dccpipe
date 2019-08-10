import hou
import os

from PySide2 import QtGui, QtWidgets, QtCore

from pipe.am.environment import Department, Environment
from pipe.am.project import Project
# from byugui.assemble_gui import AssembleWindow
from pipe.am.body import AssetType
import pipe.gui.quick_dialogs as qd
# import checkout

class CreateToolHda:

    def __init__(self):
        pass

    def run(self, node=None):
    	# global create_window
    	self.hda = node

    	if self.hda is None:
    		selection = hou.selectedNodes()
    		if len(selection) > 1:
    			qd.error('Please select only one node')
    			return
    		elif len(selection) < 1:
    			qd.error('Please select a node')
    			return
    		self.hda = selection[0]

    	create_window = AssembleWindow(hou.ui.mainQtWindow(), [Department.HDA])  # this lists hdas that have been created
    	create_window.finished.connect(create_hda)

    def create_hda(self, value):
    	tool_name = create_window.result

    	if tool_name is None:
    		return

    	if not self.hda.canCreateDigitalAsset():
    		if self.hda.type().definition is not None:
    			# we are dealing with an premade self.hda
    			result = qd.yes_or_no('The selected node is already a digial asset. Would you like to copy the definition into the pipeline')
    			if not result:
    				return
    			copyHDA = True
    		else:
    			qd.error('You can\'t make a digital asset from the selected node')
    			return
    	else:
    		copyHDA = False

    	project = Project()
    	environment = Environment()
    	username = project.get_current_username()
    	tool = project.get_tool(tool_name)
    	hda_element = tool.get_element(Department.HDA)

    	checkout_file = hda_element.checkout(username)

    	operatorName = hda_element.get_short_name()
    	operatorLabel = (project.get_name() + ' ' + tool.get_name()).title()
    	saveToLibrary = checkout_file

    	num_inputs = len(self.hda.inputs())

    	if copyHDA:
    		parent = self.hda.parent()

    		subnet = parent.createNode('subnet')

    		hda_node = subnet.createDigitalAsset(name=operatorName, description=operatorLabel, hda_file_name=saveToLibrary, min_num_inputs=num_inputs)

    		hou.copyNodesTo(self.hda.children(), hda_node)
    		hda_nodeDef = hda_node.type().definition()
    		hdaDef = self.hda.type().definition()

    		#Copy over sections
    		sects = hdaDef.sections()
    		for sectName in sects:
    			print 'Copying over section: ' + str(sectName)
    			hda_nodeDef.addSection(sectName, sects[sectName].contents())

    		#Copy over NodeGroups
    		nodeGroups = self.hda.nodeGroups()
    		for ng in nodeGroups:
    			newNg = hda_node.addNodeGroup(ng.name())
    			print 'New group: ' + str(newNg)
    			for node in ng.nodes():
    				nodePath = hda_node.path() + '/' + str(node.name())
    				print 'The Node path is:' + str(nodePath)
    				newNode = hou.node(nodePath)
    				if newNode is None:
    					print ('Ya that node was null that is a problem')
    					continue
    				print 'The new Node is: ' + str(newNode)
    				newNg.addNode(newNode)

    		# Copy over paramters
    		oldParms = hdaDef.parmTemplateGroup()
    		hda_nodeDef.setParmTemplateGroup(oldParms)
    	else:
    		try:
    			hda_node = self.hda.createDigitalAsset(name=operatorName, description=operatorLabel, hda_file_name=saveToLibrary, min_num_inputs=num_inputs)
    		except hou.OperationFailed, e:
    			print qd.error('There was a problem creating a digital asset', details=str(e))
    			return

    	assetTypeDef = hda_node.type().definition()
    	assetTypeDef.setIcon(environment.get_project_dir() + '/byu-pipeline-tools/assets/images/icons/hda-icon.png')
    	if not copyHDA:
    		nodeParms = hda_node.parmTemplateGroup()
    		assetTypeDef.setParmTemplateGroup(nodeParms)
    	hda_node.setSelected(True)
