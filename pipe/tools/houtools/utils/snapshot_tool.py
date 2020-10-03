import hou
import os

from PySide2 import QtGui, QtWidgets, QtCore
import pipe.gui.select_from_list as sfl

from pipe.am.environment import Department, Environment
from pipe.am.project import Project
from pipe.am.body import AssetType
import pipe.gui.quick_dialogs as qd
from pipe.tools.houtools.utils.utils import *

class SnapshotTool:

    def __init__(self):
        pass

    def run(self):
        self.environment = Environment()
        self.project = Project()
        hda_dir = self.environment.get_hda_dir()

        # GET LIST OF CAMERAS
        self.cameraList = hou.node('/').recursiveGlob('*', hou.nodeTypeFilter.ObjCamera)
        cameraNameList = [ camera.name() for camera in self.cameraList]

        self.item_gui = sfl.SelectFromList(l=cameraNameList, parent=houdini_main_window(), title="Select cameras to snapshot from", multiple_selection=True)
        self.item_gui.submitted.connect(self.camera_results)
        print self.item_gui

    def camera_results(self, value):
        print(str(value))
        cameras = [cam for cam in self.cameraList if cam.name() in value]

        cur_desktop = hou.ui.curDesktop()
        desktop = cur_desktop.name()
        panetab = cur_desktop.paneTabOfType(hou.paneTabType.SceneViewer)
        persp = panetab.curViewport().name()

        for cam in cameras:
            panetab.curViewport().setCamera(cam)
            default_filename = cam.name() + '_screenshot.jpg'
            persp = panetab.curViewport().name()
            filename = hou.ui.selectFile(start_directory=Project().get_submission_location(), title='Select Screenshot File', default_value=default_filename, file_type=hou.fileType.Image )
            if filename is not None:
                frame = hou.frame()
                hou.hscript( "viewwrite -f %d %d %s '%s'" % (frame, frame, (desktop + "." + panetab.name() + ".world." + persp), filename))

    # def snapshot(self):
    #     if self.asset_name:
    #         self.shapshot_results([self.asset_name])
    #         return
    #
    #     asset_list = Project().list_assets()
    #
    #     self.item_gui = sfl.SelectFromList(l=asset_list, parent=maya_main_window(), title="Which asset is this snap for?")
    #     self.item_gui.submitted.connect(self.shapshot_results)
    #
    # def camera_results(self, values):
    #     cameras = []
    #
    #     for item in values.items():
    #         if item[1]:
    #             cameras.append(item[0])
    #
    #     submission_location = Project().get_submission_location()
    #
    #     try:
    #         files = self.quick_render(submission_location, cameras)
    #     except Exception as e:
    #         qd.error("Snapshot failed: " + str(e))
    #         return
    #
    #     file_string = ""
    #     for dest in files:
    #         file_string += str(dest) + "\n"
    #
    #     qd.info("Snapshot(s) created at:\n" + file_string)
