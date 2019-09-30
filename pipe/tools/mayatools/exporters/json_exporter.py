import os, sys
import shutil
import json

import pymel.core as pm
import maya.cmds as mc
import maya.mel as mel

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
    Gets list of all referenced objects in the current scene
    Exports list to JSON file with the following info for each asset:
    asset name
    version number
    Translation/Position [X,Y,Z]
    Scale [X, Y, Z]
    Rotation [X, Y, Z]
    Each scene asset is a JSON object in a JSON array
'''
class JSONExporter:

    def __init__(self):
        self.select_from_list_dialog = None

    def confirmWriteSetReferences(self, body=None):
        filepath = pm.sceneName()
        fileDir = os.path.dirname(filepath)
        proj = Project()
        if not body:
            checkout = proj.get_checkout(fileDir)
            bodyName = checkout.get_body_name()
            body = proj.get_body(bodyName)

        if body.is_asset():
            if body.get_type() == AssetType.SET:
                print("SET OK")
                element = body.get_element(Department.MODEL)
                refsfilepath = os.path.join(Project().get_assets_dir(), element.get_cache_dir())
                self.exportReferences(refsfilepath)
                print("JSON references written successfully.")
            else:
                print("NOT A SET")
                qd.error('No set found in current scene.')

    def confirmWritePropReference(self, body=None):
        filepath = pm.sceneName()
        fileDir = os.path.dirname(filepath)
        project = Project()

        if not body:
            checkout = project.get_checkout(fileDir)
            bodyName = checkout.get_body_name()
            body = project.get_body(bodyName)

        if body.is_asset() and body.get_type() == AssetType.PROP:
            element = body.get_element(Department.MODEL)
            filepath = os.path.join(project.get_assets_dir(), element.get_cache_dir())
            assemblies = pm.ls(assemblies=True)
            pm.select(pm.listCameras(), replace=True)
            cameras = pm.selected()
            pm.select([])
            non_cameras = [assembly for assembly in assemblies if assembly not in cameras]
            self.exportPropJSON(filepath, non_cameras[0], isReference=False, name=body.get_name())
            print("JSON references written successfully.")

    def confirmWriteShotReferences(self, body=None):
        filepath = pm.sceneName()
        filDir = os.path.dirname(filepath)
        proj = Project()
        if not body:
            checkout = proj.get_checkout(fileDir)
            bodyName = checkout.get_body_name()
            body = proj.get_body(bodyName)

        if body.is_shot():
            print("SHOT OK")
            element = body.get_element(Department.ANIM)
            refsfilepath = os.path.join(Project().get_assets_dir(), element.get_cache_dir())
            self.export_shot(refsfilepath)
        else:
            print("NOT A SHOT")
            qd.error('No set found in current scene.')

    def write_animated_props(self, values):
        animated_props = values
        print "writing animated props: {0}".format(animated_props)
        animated_prop_jsons = []
        for animated_prop in animated_props:
            animated_prop_name = animated_prop.split(", version")[0]
            animated_prop_number = animated_prop.split(", version")[1]
            animated_prop_jsons.append({"asset_name" : animated_prop_name, "version_number": animated_prop_number, "animated" : True})
        if len(animated_prop_jsons) < 1:
            return
        jsonAnimatedProps = json.dumps(animated_prop_jsons)
        path = os.path.join(filepath, "animated_props.json")
        with open(path, "w") as f:
            f.write(jsonAnimatedProps)
            f.close()
        print("JSON references written successfully.")

    def export_shot(self, filepath):
        refsSelection = get_loaded_references()
        props = []
        actors = []
        sets = []

        for ref in refsSelection:
            print("ref: ", ref)
            try:
                rootNode = get_root_node_from_reference(ref)
            except:
                qd.warning("Could not find " + str(ref) + " in scene. Skipping.")
                continue

            body = get_body_from_reference(rootNode)
            currRefName, currRefVerNum = extract_reference_data(ref)

            if not body or not body.is_asset():
                print "Asset \"{0}\" does not exist.".format(currRefName)
                continue

            if body.get_type() == AssetType.PROP:
                parent_is_set = has_parent_set(rootNode)
                if parent_is_set:
                    continue
                props.append({"asset_name" : currRefName, "version_number" : int(currRefVerNum if len(currRefVerNum) > 0 else 0)})

            elif body.get_type() == AssetType.ACTOR:
                actors.append({"asset_name" : currRefName, "version_number" : int(currRefVerNum if len(currRefVerNum) > 0 else 0)})

            else:
                parent_is_set = has_parent_set(rootNode)
                if parent_is_set:
                    continue
                sets.append({"asset_name" : currRefName, "version_number" : int(currRefVerNum if len(currRefVerNum) > 0 else 0)})

        print "props: {0}\nactors: {1}\nsets: {2}".format(props, actors, sets)

        jsonActors = json.dumps(actors)
        path = os.path.join(filepath, "actors.json")

        with open(path, "w") as f:
            f.write(jsonActors)
            f.close()

        jsonSets = json.dumps(sets)
        path = os.path.join(filepath, "sets.json")

        with open(path, "w") as f:
            f.write(jsonSets)
            f.close()

        response = False  #qd.yes_or_no("Are there any animated props?")
        if not response:
            print("JSON references written successfully.")
            return

        props_and_nums = [prop["asset_name"] + ", version: " + str(prop["version_number"]) for prop in props]
        self.select_from_list_dialog = SelectFromList(parent=maya_main_window(), title="Select any animated props", l=props_and_nums, multiple_selection=True)
        self.select_from_list_dialog.submitted.connect(self.write_animated_props)

    # Creates a list of all reference files in the current set
    def exportReferences(self, filepath):
        refsSelection = get_loaded_references()
        print("refsSelection = ", refsSelection)

        allReferences = []
        for ref in refsSelection:
            try:
                rootNode = get_root_node_from_reference(ref)
            except:
                qd.warning("Could not find " + str(ref) + " in scene. Skipping.")
                continue

            print("\t Curr rootNode: ", rootNode)
            propJSON = self.exportPropJSON(filepath, rootNode)

            if propJSON:
                allReferences.append(propJSON)

        print "all References: {0}".format(allReferences)
        jsonRefs = json.dumps(allReferences)
        path = os.path.join(filepath, "whole_set.json")

        with open(path, "w") as f:
            f.write(jsonRefs)
            f.close()

    def exportPropJSON(self, filepath, rootNode, isReference=True, name="", version_number=None):
        if isReference:
            try:
                body = get_body_from_reference(rootNode)
            except:
                qd.warning("Could not find " + str(filepath) + " in scene. Skipping.")
                return None
        else:
            body = Project().get_body(name)

        if not body or not body.is_asset() or body.get_type() != AssetType.PROP:
            qd.warning("The asset " + str(rootNode) + " does not exist as a prop, skipping.")
            return None

        name = body.get_name()

        # Increment the version number
        version_number, version_string = body.version_prop_json(name, filepath)

        firstMesh, path = find_first_mesh(rootNode)
        vertpos1, vertpos2, vertpos3 = get_anchor_points(firstMesh)

        # Put all relevant data into dictionary object
        json_data = {"asset_name": name,
                     "version_number": version_number,
                     "path" : path,
                     "a" : [vertpos1.x, vertpos1.y, vertpos1.z],
                     "b" : [vertpos2.x, vertpos2.y, vertpos2.z],
                     "c" : [vertpos3.x, vertpos3.y, vertpos3.z] }

        print("json data: ", json_data)

        # Write JSON to fill
        jsonRef = json.dumps(json_data)
        wholePath = os.path.join(filepath, os.path.join(filepath, name + "_" + version_string + ".json"))
        outfile = open(wholePath, "w")  # *** THIS IS THE NAME OF THE OUTPUT FILE ***
        outfile.write(jsonRef)
        outfile.close()

        if not isReference:
            print("JSON references written successfully.")

        return {"asset_name" : json_data["asset_name"], "version_number" :  json_data["version_number"]}

    def go(self, body, type):
        if type == AssetType.SHOT:
            self.confirmWriteShotReferences(body)
        elif type == AssetType.PROP:
            self.confirmWritePropReference(body)
        elif type == AssetType.SET:
            self.confirmWriteSetReferences(body)
        else:
            print("No JSON exported because this is a actor.")
