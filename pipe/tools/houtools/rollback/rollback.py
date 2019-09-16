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


class Rollback:

    def __init__(self):
        self.node = None
        self.publishes = None
        self.sanitized_publish_list = None
        self.item_gui = None

    def rollback_element(self, node, department, name):
        self.node = node

        project = Project()
        body = project.get_body(name)
        element = body.get_element(department)

        self.publishes = element.list_publishes()
        print("publishes: ", self.publishes)

        if not self.publishes:
            qd.error("There have been no publishes for this department. Rollback failed.")
            return

        # make the list a list of strings, not tuples
        self.sanitized_publish_list = []
        for publish in self.publishes:
            path = publish[3]
            file_ext = path.split('.')[-1]
            if not file_ext == "hda" and not file_ext =="hdanc":
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

        print("selected file: ", selected_scene_file)
        definitions = hou.hda.definitionsInFile(selected_scene_file)
        definition = definitions[0]

        source_path = self.node.type().sourcePath()
        hou.hda.installFile(selected_scene_file)
        definition.setPreferred(True)

        print("node: ", self.node, str(self.node))
        type = self.node.type().name()
        print("type: ", str(type))

        parent = self.node.parent()
        new_node = parent.createNode(str(type))

        try:
            self.node.type().definition().updateFromNode(new_node)
        except hou.OperationFailed, e:
            qd.error('There was a problem during rollback.\n')
            print(str(e))
            return

        try:
            self.node.matchCurrentDefinition()  # this function locks the node for editing.
        except hou.OperationFailed, e:
            qd.warning('There was a problem while trying to match the current definition.')
            print(str(e))

        self.node.allowEditingOfContents()
        new_node.destroy()

    def rollback_asset(self, node=None):
        pass

    def rollback_tool(self, node=None):
        pass

    def rollback_shot(self):
        pass
