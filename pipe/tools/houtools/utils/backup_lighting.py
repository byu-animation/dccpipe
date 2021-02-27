import hou
import os
from datetime import datetime

from PySide2 import QtGui, QtWidgets, QtCore

from pipe.am.environment import Department, Environment
from pipe.am.project import Project
from pipe.am.body import AssetType
import pipe.gui.quick_dialogs as qd
from pipe.tools.houtools.utils.utils import *

class BackupLighting:

    def __init__(self):
        pass

    def go(self, node=None):
        path = hou.hscriptExpression("$HIP")
        path = path[:path.find("main/") + 5] + "cache/lightlinking.json"
        command = "objlightlink -e " + str(path)

        print("Backing up light linking to " + str(path))
        result = hou.hscript(command)
        print(result)
