#from pipe.gui.reference_gui import ReferenceWindow
import pipe.gui.quick_dialogs as qd
from pipe.am.environment import Department
from pipe.am.pipeline_io import *
import pipe.gui.select_from_list as sfl
from pipe.tools.mayatools.utils.utils import *

import pymel.core as pm
from PySide2 import QtWidgets
import maya.OpenMayaUI as omu
import os
import time


class MayaReferencer:

    def __init__(self):
        self.item_gui = None

    def reference_prop_or_actor(self):
        self.project = Project()
        asset_list = self.project.list_props_and_actors()

        self.item_gui = sfl.SelectFromList(l=asset_list, parent=maya_main_window(), title="What do you want to reference?", multiple_selection=True)
        self.item_gui.submitted.connect(self.post_reference)

    def reference_prop(self):
        self.project = Project()
        asset_list = self.project.list_props()

        self.item_gui = sfl.SelectFromList(l=asset_list, parent=maya_main_window(), title="What do you want to reference?", multiple_selection=True)
        self.item_gui.submitted.connect(self.post_reference)

    def reference_actor(self):
        self.project = Project()
        asset_list = self.project.list_actors()

        self.item_gui = sfl.SelectFromList(l=asset_list, parent=maya_main_window(), title="What do you want to reference?", multiple_selection=True)
        self.item_gui.submitted.connect(self.post_reference)

    def reference_set(self):
        self.project = Project()
        asset_list = self.project.list_sets()

        self.item_gui = sfl.SelectFromList(l=asset_list, parent=maya_main_window(), title="What do you want to reference?", multiple_selection=True)
        self.item_gui.submitted.connect(self.post_reference)

    def reference_any(self):
        self.project = Project()
        asset_list = self.project.list_assets()

        self.item_gui = sfl.SelectFromList(l=asset_list, parent=maya_main_window(), title="What do you want to reference?", multiple_selection=True)
        self.item_gui.submitted.connect(self.post_reference)

    def post_reference(self, value):
        assets = value
        asset_filepaths = []

        # TODO: add crowd cycle capability
        crowd = False  # qd.yes_or_no("Are you referencing a crowd cycle?")

        if crowd:
            self.reference_crowd_cycle(asset_filepaths)
        else:

            for asset in assets:
                body = self.project.get_body(asset)

                # TODO: change the choice to depend more on each individual asset. I.e. only ask model or rig for actors. Otherwise it's always going to be model.
                type = body.get_type()
                if type == AssetType.ACTOR:
                    model = qd.binary_option("Which department for " + str(asset) + "?", "Model", "Rig", title="Select department")
                else:
                    model = True

                if model:
                    department = "model"
                elif model is not None:
                    department = "rig"
                else:
                    qd.warning("Skipping " + str(asset))
                    continue

                element = body.get_element(department)
                filepath = element.get_app_filepath()

                if filepath:
                    asset_filepaths.append(filepath)

                else:
                    qd.warning("No publish exists for " + str(asset) + " in " + str(department) + ". Skipping.")

            print("files for reference: ", asset_filepaths)
            self.reference_asset(asset_filepaths)

    def reference_asset(self, filepath_list):
        if filepath_list is not None:
            for path in filepath_list:
                print("Path: ", path)
                if os.path.exists(path):
                    print (path, " exists")
                    part_one, part_two = path.split("assets/")
                    asset = part_two.split("/")[0]

                    while True:
                        try:
                            num_references = int(qd.input("How many copies of " + str(asset) + " do you want to reference?"))
                        except:
                            qd.warning("Invalid input for " + str(asset) + ". Try again.")
                            continue
                        break

                    for i in range(num_references):
                        pm.system.createReference(path, namespace=asset)
                else:
                    qd.warning(path, " doesn't exist")

    def reference_crowd_cycle(self, paths):  # TODO: this needs work. I haven't looked over or tested this yet.
        pm.loadPlugin('AbcImport')
        for cycle in paths:
            if not os.path.exists(cycle):
                print 'this is the type', type(cycle)
                print 'The cycle doesn\'t exist. That seems weird.', cycle
                print os.path.exists(str(cycle)), 'this is another shot'
                return
            fileName = os.path.basename(cycle)
            #The file is going to be an alembic so we can drop the last four actors '.abc' to get the file name
            cycleName = fileName[:len(fileName)-4]

            invalidInput = True
            while(invalidInput):
                try:
                    refCount = int(qd.input('How many times do you want to reference this cycle?'))
                except ValueError:
                    qd.error('Please enter a number')
                    continue
                invalidInput = False

            for i in range(refCount):
                time.sleep(1) # sleep for a bit to make sure out namespace is unique
                time = timestamp()
                namespace = cycleName + str(time)

                cycleRefGroup = namespace + 'RNgroup'
                cycleControls = namespace + '_controls'
                offset = 'offset'
                speed = 'speed'
                cycleType = 'cycleType'
                translate = 'translate'
                rotate = 'rotate'
                scale = 'scale'
                refAlembicNode = namespace + ':' + cycleName + '_AlembicNode'
                refAlembicOffset = refAlembicNode + '.' + offset
                refAlembicSpeed = refAlembicNode + '.' + speed
                refAlembicCycleType = refAlembicNode + '.' + cycleType
                controlAlembicOffset = cycleControls + '.' + offset
                controlAlembicSpeed = cycleControls + '.' + speed

                cycleRefTranslate = cycleRefGroup + '.' + translate
                cycleRefScale = cycleRefGroup + '.' + scale
                cycleRefRotate = cycleRefGroup + '.' + rotate

                controlAlembicTranslate = cycleControls + '.' + translate
                controlAlembicScale = cycleControls + '.' + scale
                controlAlembicRotate = cycleControls + '.' + rotate

                pm.system.createReference(cycle, groupReference=True, namespace=namespace)

                node = pm.ls(cycleRefGroup)[0]
                circ = pm.circle(r=0.25,nr=(0, 1, 0), n=cycleControls)[0]
                parentGroupName = namespace + 'agent'
                group = pm.group(name=parentGroupName, em=True)

                pm.parent(circ, group)
                pm.parent(node, group)

                if circ.hasAttr(offset):
                    circ.deleteAttr(offset)
                if circ.hasAttr(speed):
                    circ.deleteAttr(speed)
                circ.addAttr(offset, at='double', hidden=False, dv=0.0, k=True)
                circ.addAttr(speed, at='double', hidden=False, dv=1.0, k=True)

                # Add agent tag so the exporter can easily find it
                crowdAgentFlag = 'BYU_Crowd_Agent_Flag'
                if group.hasAttr(crowdAgentFlag):
                    group.deleteAttr(crowdAgentFlag)
                group.addAttr(crowdAgentFlag, at=bool, hidden=False, dv=True, k=True)

                # When passing in arguments to connectAttr remember that attr 1 controls attr 2
                pm.connectAttr(controlAlembicOffset, refAlembicOffset)
                pm.connectAttr(controlAlembicSpeed, refAlembicSpeed)
                pm.setAttr(refAlembicCycleType, 1)
                pm.connectAttr(controlAlembicTranslate, cycleRefTranslate)
                pm.connectAttr(controlAlembicRotate, cycleRefRotate)
                pm.connectAttr(controlAlembicScale, cycleRefScale)

    def dereference_assets(self):
        self.references = get_loaded_references()
        ref_names = []
        for ref in self.references:
            ref_names.append(str(ref))

        self.item_gui = sfl.SelectFromList(l=ref_names, parent=maya_main_window(), title="Select Assets to Unload", multiple_selection=True)
        self.item_gui.submitted.connect(self.dereference_asset)

    def dereference_asset(self, reference_names):
        for name in reference_names:
            for ref in self.references:
                if str(ref) == name:
                    unload_reference(ref)
