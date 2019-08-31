import maya.cmds as mc
import maya.mel as mel
import os
import shutil

from pipe.am.project import Project
from pipe.am.environment import Environment, Department
import pipe.am.pipeline_io
import pipe.gui.quick_dialogs as qd
import pipe.gui.select_from_list as sfl
from pipe.tools.mayatools.utils.utils import *


class Playblaster:
    def __init__(self):
        pass

    def playblast(self):
        asset_list = Project().list_assets()

        self.item_gui = sfl.SelectFromList(l=asset_list, parent=maya_main_window(), title="Select an asset to playblast")
        self.item_gui.submitted.connect(self.asset_results)

    def asset_results(self, value):
        chosen_asset = value[0]

        project = Project()
        self.body = project.get_body(chosen_asset)

    	start_frame = mc.playbackOptions(q=True, min=True)
    	end_frame = mc.playbackOptions(q=True, max=True)

        playblast_element = self.body.get_element(Department().RENDER)
        playblast_dir = playblast_element.get_render_dir()
        playblast_filename = chosen_asset + "_playblast.mov"
        path = os.path.join(playblast_dir, playblast_filename)

    	self.simpleBlast(start_frame, end_frame, path)
        qd.info("Playblast created at " + str(path))

    def simpleBlast(self, start_frame, end_frame, filename):
    	mc.playblast(st=start_frame, et=end_frame, fmt="qt", compression="png", qlt=100, forceOverwrite=True, filename=filename, offScreen=True, percent=100, v=False)
        pipeline_io.set_permissions(filename)

        return
