import hou
import os

from PySide2 import QtGui, QtWidgets, QtCore

from pipe.am.environment import Department, Environment
from pipe.am.project import Project
from pipe.am.body import AssetType
import pipe.gui.quick_dialogs as qd
from pipe.tools.houtools.utils.utils import *

class CreateToolHda:

    def __init__(self):
        pass

    def go(self, node=None):
        self.hda = node
        environment = Environment()
        project = Project()
        hda_dir = environment.get_hda_dir()

        if self.hda is None:
            self.hda = get_selected_node()
            if self.hda is None:
                return

        node_path = self.hda.path()
        name = node_path.split('/')[-1]
        tool_name = name.lower()

        if tool_name is None:
            return

        if not self.hda.canCreateDigitalAsset():
            if self.hda.type().definition is not None:
                # we are dealing with an premade self.hda
                result = qd.yes_or_no('The selected node is already a digial asset. Would you like to copy the definition into the pipeline')
                if not result:
                    return
                else:
                    copyHDA = True
            else:
                qd.error('You can\'t make a digital asset from the selected node')
                return
        else:
            copyHDA = False

        destination = os.path.join(hda_dir, tool_name + ".hda")

        operatorName = tool_name
        operatorLabel = str(project.get_name()) + '_' + str(tool_name)
        saveToLibrary = destination
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
                hda_nodeDef.addSection(sectName, sects[sectName].contents())

            #Copy over NodeGroups
            nodeGroups = self.hda.nodeGroups()
            for ng in nodeGroups:
                newNg = hda_node.addNodeGroup(ng.name())

                for node in ng.nodes():
                    nodePath = hda_node.path() + '/' + str(node.name())
                    newNode = hou.node(nodePath)

                    if newNode is None:
                        print ('Ya that node was null that is a problem')
                        continue

                    newNg.addNode(newNode)

            # Copy over paramters
            oldParms = hdaDef.parmTemplateGroup()
            hda_nodeDef.setParmTemplateGroup(oldParms)
        else:
            try:
                hda_node = self.hda.createDigitalAsset(name=operatorName, description=operatorLabel, hda_file_name=saveToLibrary, min_num_inputs=num_inputs)
            except hou.OperationFailed, e:
                qd.error('There was a problem creating a digital asset', details=str(e))
                return

        assetTypeDef = hda_node.type().definition()
        assetTypeDef.setIcon(environment.get_project_dir() + '/byu-pipeline-tools/assets/images/icons/hda-icon.png')

        if not copyHDA:
            nodeParms = hda_node.parmTemplateGroup()
            assetTypeDef.setParmTemplateGroup(nodeParms)

        hda_node.setSelected(True)
