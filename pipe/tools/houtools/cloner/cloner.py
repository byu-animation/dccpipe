import hou
import os
# from PySide2 import QtGui, QtWidgets, QtCore
import pipe.gui.quick_dialogs as qd
import pipe.gui.select_from_list as sfl

from pipe.tools.houtools.utils.utils import *
from pipe.tools.houtools.importer.importer import Importer

from pipe.am.project import Project
from pipe.am.body import Body
from pipe.am.element import Element
from pipe.am.environment import Department
from pipe.am.environment import Environment
from pipe.tools.houtools.assembler.assembler import Assembler


class Cloner:

    def __init__(self):
        self.item_gui = None
        self.modify_publish = None
        self.material_publish = None
        self.hair_publish = None
        self.cloth_publish = None
        environment = Environment()
        self.user = environment.get_user()

    def clone_asset(self, node=None):
        self.clone_hda(hda=node)

    def clone_tool(self, node=None):
        self.project = Project()
        hda_list = self.project.list_hdas()

        self.item_gui = sfl.SelectFromList(l=hda_list, parent=houdini_main_window(), title="Select a tool to clone")
        self.item_gui.submitted.connect(self.tool_results)

    def tool_results(self, value):
        tool_name = value[0]

        source = os.path.join(Environment().get_hda_dir(), str(tool_name) + ".hda")

        hou.hda.installFile(source)
        obj = hou.node("/obj")
        hda = obj.createNode(tool_name)
        definition = hou.hdaDefinition(hda.type().category(), hda.type().name(), source)
        definition.setPreferred(True)

        hda.allowEditingOfContents()

        try:
            hda.setName(tool_name)
        except:
            qd.warning(str(tool_name) + " cloned but could not be renamed correctly.")

        layout_object_level_nodes()

    def clone_shot(self):
        project = Project()

        asset_list = project.list_shots()
        self.item_gui = sfl.SelectFromList(l=asset_list, parent=houdini_main_window(), title="Select a shot to clone")
        self.item_gui.submitted.connect(self.shot_results)

    def shot_results(self, value):
        shot_name = value[0]
        project = Project()

        body = project.get_body(shot_name)
        element = body.get_element("lighting")

        self.publishes = element.list_publishes();
        print("publishes: ", self.publishes)

        if not self.publishes:
            # has not been imported. Import it first.
            importer = Importer()
            importer.import_shot([shot_name])
            return

        # make the list a list of strings, not tuples
        self.sanitized_publish_list = []
        for publish in self.publishes:
            path = publish[3]
            file_ext = path.split('.')[-1]
            if not file_ext == "hip" and not file_ext == "hipnc":
                continue
            label = publish[0] + " " + publish[1] + " " + publish[2]
            self.sanitized_publish_list.append(label)

        self.item_gui = sfl.SelectFromList(l=self.sanitized_publish_list, parent=houdini_main_window(), title="Select publish to clone")
        self.item_gui.submitted.connect(self.publish_selection_results)

    def publish_selection_results(self, value):

        selected_publish = None
        for item in self.sanitized_publish_list:
            if value[0] == item:
                selected_publish = item

        selected_scene_file = None
        for publish in self.publishes:
            label = publish[0] + " " + publish[1] + " " + publish[2]
            if label == selected_publish:
                selected_scene_file = publish[3]

        if selected_scene_file is not None:
            if not os.path.exists(selected_scene_file):
                qd.error('Filepath doesn\'t exist')
                return
            else:
                hou.hipFile.load(selected_scene_file)

    def clone_hda(self, hda=None):
        project = Project()

        asset_list = project.list_props_and_actors()
        self.item_gui = sfl.SelectFromList(l=asset_list, parent=houdini_main_window(), title="Select an asset to clone")
        self.item_gui.submitted.connect(self.asset_results)

    def asset_results(self, value):
        print("Selected asset: ", value[0])
        filename = value[0]

        return Assembler().clone_content_hdas(filename);
