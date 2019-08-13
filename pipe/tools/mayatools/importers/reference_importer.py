from pipe.am.environment import Environment
import pipe.gui.select_from_list as sfl
from pipe.tools.mayatools.utils.utils import *

import maya.cmds as cmds
import os


class ReferenceImporter:
    def __init__(self):
        self.item_gui = None

    def go(self):
        environment = Environment()
        reference_dir = environment.get_reference_geo_dir()
        files = os.listdir(reference_dir)

        self.item_gui = sfl.SelectFromList(l=files, parent=maya_main_window(), title="Select reference character(s) to import", multiple_selection=True)
        self.item_gui.submitted.connect(self.results)

    def results(self, files):
        for file in files:
            cmds.file( file, i = True, type="OBJ", iv=True, ra=True, mnc=False, ns="reference_object", op="mo=1", pr=True)
