import sys, os, json
import shutil
import json

import hou

from pipe.gui import quick_dialogs
from pipe.gui.select_from_list import SelectFromList
from pipe.am.project import Project
from pipe.am.body import AssetType
from pipe.am.environment import Environment, Department  # , Status

from PySide2 import QtCore
from PySide2 import QtWidgets
from PySide2.QtCore import Signal, Slot


'''
    This class is necessary for sets created and published from Houdini
    because the way sets usually work is from Maya, however if we want Maya sets and Houdini sets
    to work together, we need them both to be compatible with each other.
    Hence, we have to write JSON files for houdini-specific sets too.
'''
class JSONExporter:

    def __init__(self):
        self.select_from_list_dialog = None

    def createWholeSetJSON(self, filepath):
        # create an empty whole_set.JSON file
        print("creating empty whole_set.json")
        path = os.path.join(filepath, "whole_set.json")

        with open(path, "w") as f:
            f.write("{}")
            f.close()


    def exportReferences(self, filepath):
        # export whole_set.json
        print("exporting references")
        #1. get list of nodes in the DCC Set node
        currentNode = ""
        setPath = ""
        try:
            currentNode = hou.selectedNodes()
            if len(currentNode) > 1:
                raise Exception("More than one node selected!")
            setPath = currentNode[0].path()

        except Exception as e:
            qd.error("please select the set node you're trying to publish", details=str(e))

        insideNode = currentNode.children()
        currentNode = insideNode[0]
        propNodes = currentNode.children()
        print("Path to Set: " + str(currentNode.path()))
        print("Nodes inside the set: " + str(propNodes))

        #2. get the name of the assets for each
        propList = []

        for node in propNodes:
            #print(node)
            name = node.parm('asset_name').eval()
            #3. make that into a list
            propList.append(name)
            print(name)
        print("\n\n")


        print(propList)

        #4. write that to JSON


    def exportPropJSON(self, filepath, rootNode, isReference=True, name="", version_number=None):
        #export props to their own JSON filepaths
        print("exporting prop JSON")
