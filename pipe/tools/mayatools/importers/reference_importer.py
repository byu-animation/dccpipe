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
        self.reference_dir = environment.get_reference_geo_dir()
        files = os.listdir(self.reference_dir)

        self.item_gui = sfl.SelectFromList(l=files, parent=maya_main_window(), title="Select reference actor(s) to import", multiple_selection=True)
        self.item_gui.submitted.connect(self.results)

    def results(self, files):
        for file in files:
            try:
                path = os.path.join(self.reference_dir, file)
                name, ext = os.path.splitext(file)
                cmds.file( path, i = True, type="OBJ", iv=True, ra=True, ns=name, op="mo=1", pr=True)

            except Exception as e:
                qd.warning(str(e))
