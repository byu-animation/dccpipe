from pipe.gui import quick_dialogs
from pipe.gui.select_from_list import SelectFromList

import os, sys
import shutil
import json

from pipe.tools.mayatools.utils.utils import *

import pymel.core as pm
import maya.cmds as mc
import maya.mel as mel

from pipe.am import *
from pipe.am.project import Project
from pipe.am import pipeline_io

# import reference_selection
# from byugui import selection_gui, message_gui, item_list
from pipe.am.body import AssetType
from pipe.am.environment import Environment, Department  # , Status
# import publish
# from byugui.publish_gui import PublishWindow

from PySide2 import QtCore
from PySide2 import QtWidgets
from PySide2.QtCore import Signal, Slot


# Gets list of all referenced objects in the current scene
# Exports list to JSON file with the following info for each asset:
# asset name
# version number
# Translation/Position [X,Y,Z]
# Scale [X, Y, Z]
# Rotation [X, Y, Z]
# Each scene asset is a JSON object in a JSON array

class JSONExporter:

    def __init__(self):
        self.select_from_list_dialog = None

    def confirmWriteSetReferences(self, body=None):
        filePath = pm.sceneName()
        fileDir = os.path.dirname(filePath)
        proj = Project()
        if not body:
            checkout = proj.get_checkout(fileDir)
            bodyName = checkout.get_body_name()
            body = proj.get_body(bodyName)

        if body.is_asset():
            if body.get_type() == AssetType.SET:
                print("SET OK")
                element = body.get_element(Department.MODEL)
                refsFilePath = os.path.join(Project().get_assets_dir(), element.get_cache_dir())
                self.exportReferences(refsFilePath)
                qd.info("JSON references written successfully.")
            else:
                print("NOT A SET")
                qd.error('No set found in current scene.')

    def confirmWritePropReference(self, body=None):
        filePath = pm.sceneName()
        fileDir = os.path.dirname(filePath)
        project = Project()

        if not body:
            checkout = project.get_checkout(fileDir)
            bodyName = checkout.get_body_name()
            body = project.get_body(bodyName)

        if body.is_asset() and body.get_type() == AssetType.PROP:
            element = body.get_element(Department.MODEL)
            filePath = os.path.join(project.get_assets_dir(), element.get_cache_dir())
            assemblies = pm.ls(assemblies=True)
            pm.select(pm.listCameras(), replace=True)
            cameras = pm.selected()
            pm.select([])
            non_cameras = [assembly for assembly in assemblies if assembly not in cameras]
            self.exportPropJSON(filePath, non_cameras[0], isReference=False, name=body.get_name())
            qd.info("JSON references written successfully.")

    def confirmWriteShotReferences(self, body=None):
        filePath = pm.sceneName()
        filDir = os.path.dirname(filePath)
        proj = Project()
        if not body:
            checkout = proj.get_checkout(fileDir)
            bodyName = checkout.get_body_name()
            body = proj.get_body(bodyName)

        if body.is_shot():
            print("SHOT OK")
            element = body.get_element(Department.ANIM)
            refsFilePath = os.path.join(Project().get_assets_dir(), element.get_cache_dir())
            self.export_shot(refsFilePath)
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
        path = os.path.join(filePath, "animated_props.json")
        with open(path, "w") as f:
            f.write(jsonAnimatedProps)
            f.close()
        qd.info("JSON references written successfully.")

    def export_shot(self, filePath):
        refsSelection = get_loaded_references()
        props = []
        characters = []
        sets = []

        for ref in refsSelection:
            rootNode = get_root_node_from_reference(ref)
            body = get_body_from_reference(rootNode)

            if not body or not body.is_asset():
                print "Asset \"{0}\" does not exist.".format(currRefName)
                continue

            if body.get_type() == AssetType.PROP:
                props.append({"asset_name" : currRefName, "version_number" : int(currRefVerNum if len(currRefVerNum) > 0 else 0)})
            elif body.get_type() == AssetType.CHARACTER:
                characters.append({"asset_name" : currRefName, "version_number" : int(currRefVerNum if len(currRefVerNum) > 0 else 0)})
            else:
                parent_is_set = has_parent_set(rootNode)
                if parent_is_set:
                    continue
                sets.append({"asset_name" : currRefName, "version_number" : int(currRefVerNum if len(currRefVerNum) > 0 else 0)})

        print "props: {0}\ncharacters: {1}\nsets: {2}".format(props, characters, sets)

        jsonCharacters = json.dumps(characters)
        path = os.path.join(filePath, "characters.json")

        with open(path, "w") as f:
            f.write(jsonCharacters)
            f.close()

        jsonSets = json.dumps(sets)
        path = os.path.join(filePath, "sets.json")

        with open(path, "w") as f:
            f.write(jsonSets)
            f.close()

        response = qd.yes_or_no("Are there any animated props?")
        if not response:
            qd.info("JSON references written successfully.")
            return

        props_and_nums = [prop["asset_name"] + ", version: " + str(prop["version_number"]) for prop in props]
        self.select_from_list_dialog = SelectFromList(parent=maya_main_window(), title="Select any animated props", l=props_and_nums, multiple_selection=True)
        self.select_from_list_dialog.submitted.connect(self.write_animated_props)

    # Creates a list of all reference files in the current set
    def exportReferences(self, filePath):
        refsSelection = get_loaded_references()
        print("refsSelection = ", refsSelection)

        allReferences = []
        for ref in refsSelection:
            rootNode = get_root_node_from_reference(ref)
            print("\t Curr rootNode: ", rootNode)
            propJSON = self.exportPropJSON(filePath, rootNode)

            if propJSON:
                allReferences.append(propJSON)

        print "all References: {0}".format(allReferences)
        jsonRefs = json.dumps(allReferences)
        path = os.path.join(filePath, "whole_set.json")

        with open(path, "w") as f:
            f.write(jsonRefs)
            f.close()

    def exportPropJSON(self, filePath, rootNode, isReference=True, name="", version_number=None):
        if isReference:
            body = get_body_from_reference(rootNode)
        else:
            body = Project().get_body(name)

        if not body or not body.is_asset() or body.get_type() != AssetType.PROP:
            print "The asset %s does not exist as a prop, skipping.".format(name)
            return None

        # Check if verNum is nothing - if so, we need to make it be an int 0
        if not version_number:
            version_number = 0

        firstMesh, path = find_first_mesh(rootNode)
        vertpos1, vertpos2, vertpos3 = get_anchor_points(firstMesh)

        # Put all relevant data into dictionary object
        json_data = {"asset_name": name,
                     "version_number": version_number,
                     "path" : path,
                     "a" : [vertpos1.x, vertpos1.y, vertpos1.z],
                     "b" : [vertpos2.x, vertpos2.y, vertpos2.z],
                     "c" : [vertpos3.x, vertpos3.y, vertpos3.z] }

        # Write JSON to fill
        jsonRef = json.dumps(json_data)
        wholePath = os.path.join(filePath, os.path.join(filePath, name + "_" + str(version_number) + ".json"))
        outfile = open(wholePath, "w")  # *** THIS IS THE NAME OF THE OUTPUT FILE ***
        outfile.write(jsonRef)
        outfile.close()

        if not isReference:
            qd.info("JSON references written successfully.")

        return {"asset_name" : json_data["asset_name"], "version_number" :  json_data["version_number"]}

    def go(self, body, type):
        if type == AssetType.SHOT:
            self.confirmWriteShotReferences(body)
        elif type == AssetType.PROP:
            self.confirmWritePropReference(body)
        elif type == AssetType.SET:
            self.confirmWriteSetReferences(body)
        else:
            print("No JSON exported because this is a character.")


    # def export_prop(self):
    #     prop_node = maya_utils.get_top_level_nodes()[0]
    #     json_cache_dir = self.json_cache_dir(self.body)
    #     name = self.body.get_name()
    #     version_number = 0
    #     json_data = self.prop_JSON_data(prop_node, name, version_number)
    #     json_cache_filepath = os.path.join(json_cache_dir, self.json_filename(name, version_number))
    #     with open(json_cache_filepath, "w") as f:
    #         f.write(json.dumps(json_data))
    #         f.close()
    #
    # def export_char(self):
    #     if self.publish_data["gui"]:
    #         quick_dialogs.warning("Exporting JSON files for static characters is not supported at this time.")
    #     else:
    #         print "{0} is a character. No JSON was exported.".format(self.body.get_name())
    #
    # def export_set(self):
    #     json_cache_dir = self.json_cache_dir(self.body)
    #     references = maya_utils.get_loaded_references()
    #     set_json_data = []
    #     for ref in references:
    #         prop_node = maya_utils.get_root_node_from_reference(ref)
    #         name, version_number = maya.extract_reference_data(ref)
    #         prop_json_data = self.prop_JSON_data(prop_node, name, version_number)
    #         set_json_data.append(prop_json_data)
    #     json_cache_filepath = os.path.join(json_cache_dir, "whole_set.json")
    #     with open(json_cache_filepath, "w") as f:
    #         f.write(json.dumps(json_cache_filepath))
    #         f.close()
    #
    # def export_shot(self):
    #     json_cache_dir = self.json_cache_dir(self.body)
    #     references = maya_utils.get_loaded_references()
    #     sets_json_data = []
    #     chars_json_data = []
    #     props_json_data = []
    #     project = Project()
    #     for ref in references:
    #         node = maya_utils.get_root_node_from_reference(ref)
    #         name, version_number = maya.extract_reference_data(ref)
    #         reference_body = project.get_body(name)
    #         if not reference_body or not reference_body.is_asset():
    #             continue
    #         if reference_body.get_type() == AssetType.SET and not maya_utils.has_parent_set(node):
    #             sets_json_data.append(self.general_JSON_data(name, version_number))
    #         elif reference_body.get_type() == AssetType.CHARACTER and maya_utils.children_tagged_with_flag(node, ExportFlags.EXPORT):
    #             chars_json_data.append(self.general_JSON_data(name, version_number))
    #         elif reference_body.get_type() == AssetType.PROP and maya_utils.children_tagged_with_flag(node, ExportFlags.EXPORT):
    #             props_json_data.append(self.prop_JSON_data(node, name, version_number))
    #     sets_json_cache_filepath = os.path.join(json_cache_dir, "sets.json")
    #     chars_json_cache_filepath = os.path.join(json_cache_dir, "characters.json")
    #     props_json_cache_filepath = os.path.join(json_cache_dir, "animated_props.json")
    #
    #     with open(sets_json_cache_filepath, "w") as f:
    #         f.write(sets_json_data)
    #         f.close()
    #     with open(chars_json_cache_filepath, "w") as f:
    #         f.write(chars_json_data)
    #         f.close()
    #     with open(props_json_cache_filepath, "w") as f:
    #         f.write(props_json_data)
    #         f.close()
    #
    # def general_JSON_data(self, name, version_number):
    #     return {
    #         "asset_name" : name,
    #         "version_number" : version_number,
    #         }
    #
    # def prop_JSON_data(self, root_node, name, version_number):
    #     mesh = maya_utils.find_first_mesh(root_node)
    #     json_data = self.general_JSON_data(name, version_number)
    #     json_data.update(maya_utils.get_anchor_points(mesh))
    #     return json_data
    #
    # def json_cache_dir(self):
    #     element = self.body.get_element(Department.MODEL)
    #     filepath = os.path.join(Project().get_assets_dir(), element.get_cache_dir)
    #     return filepath
    #
    # def json_filename(name, version_number):
    #     return name + "_" + str(version_number) + ".json"
