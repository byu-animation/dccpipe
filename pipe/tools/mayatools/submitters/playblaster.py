import maya.cmds as mc
import maya.mel as mel

import os
import shutil

from pipe.am.project import Project
from pipe.am.environment import Environment, Department
import pipe.am.pipeline_io
import pipe.gui.quick_dialogs as qd
import pipe.gui.select_from_list as sfl
import pipe.gui.checkbox_options as co
from pipe.tools.mayatools.utils.utils import *


class Playblaster:
    def __init__(self):
        self.asset_name = os.environ.get("DCC_ASSET_NAME")

    def playblast(self):
        if self.asset_name:
            self.asset_results([self.asset_name])
            return

        asset_list = Project().list_assets()

        self.item_gui = sfl.SelectFromList(l=asset_list, parent=maya_main_window(), title="Which asset is this blast for?")
        self.item_gui.submitted.connect(self.asset_results)

    def asset_results(self, value):
        chosen_asset = value[0]

        start_frame = mc.playbackOptions(q=True, min=True)
        end_frame = mc.playbackOptions(q=True, max=True)

        submission_location = Project().get_submission_location()
        playblast_filename = chosen_asset + "_playblast.mov"
        path = os.path.join(submission_location, playblast_filename)

        try:
            self.simple_blast(start_frame, end_frame, path)
        except Exception as e:
            qd.error("playblast failed: " + str(e))
            return

        qd.info("Playblast created at " + str(path))

    def simple_blast(self, start_frame, end_frame, filename):
        mc.playblast(st=start_frame, et=end_frame, fmt="qt", compression="jpeg", qlt=100, forceOverwrite=True, filename=filename, offScreen=True, percent=100, v=False)
        pipeline_io.set_permissions(filename)

    def snapshot(self):
        if self.asset_name:
            self.shapshot_results([self.asset_name])
            return

        asset_list = Project().list_assets()

        self.item_gui = sfl.SelectFromList(l=asset_list, parent=maya_main_window(), title="Which asset is this snap for?")
        self.item_gui.submitted.connect(self.shapshot_results)

    def shapshot_results(self, value):
        self.chosen_asset = value[0]
        cam_list = mc.listCameras()

        self.item_gui = co.CheckBoxOptions(parent=maya_main_window(), title="Select cameras to use:", options=cam_list)
        self.item_gui.submitted.connect(self.camera_results)

    def camera_results(self, values):
        cameras = []

        for item in values.items():
            if item[1]:
                cameras.append(item[0])

        submission_location = Project().get_submission_location()

        try:
            files = self.quick_render(submission_location, cameras)
        except Exception as e:
            qd.error("Snapshot failed: " + str(e))
            return

        file_string = ""
        for dest in files:
            file_string += str(dest) + "\n"

        qd.info("Snapshot(s) created at:\n" + file_string)

    def quick_render(self, location, cameras):
        # set image format to jpg
        mc.setAttr("defaultRenderGlobals.imageFormat", 8)

        # get the directory where the images will be created
        projectDirectory = mc.workspace(q=True, rd=True)
        scene_name = mc.file(q=True, sn=True, shn=True)
        scene_name = os.path.splitext(scene_name)[0]
        image_path = os.path.join(projectDirectory, "images", "tmp", scene_name + ".jpg")

        # create the render for each image, move it to the location specified in project settings
        paths = []
        for camera in cameras:
            filename = self.chosen_asset + "_" + camera + ".jpeg"
            path = os.path.join(location, filename)

            mc.hwRender(cf=True, nrv=False, cam=camera, lql=True, eaa=[0,3])
            shutil.move(image_path, path)
            pipeline_io.set_permissions(path)
            paths.append(path)

        return paths

    def set_submission_location(self):
        submission_location = Project().get_submission_location()

        option = qd.yes_or_no("Current location is:\n" + str(submission_location) + "\nSet new submission location?")

        if option:
            new_location = qd.input("New location: ")
        else:
            return

        if new_location and not new_location == "":
            Project().set_submission_location(new_location)
