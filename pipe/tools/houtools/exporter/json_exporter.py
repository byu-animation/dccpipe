import sys, os, json
import shutil
import json

import hou

from pipe.gui import quick_dialogs
from pipe.gui.select_from_list import SelectFromList
from pipe.tools.mayatools.utils.utils import *
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

    def exportReferences(self, filepath):
        # export whole_set.json
        print("exporting references")

    def exportPropJSON(self, filepath, rootNode, isReference=True, name="", version_number=None):
        #export props to their own JSON filepaths
        print("exporting prop JSON")
