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
        self.department = department

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

    def get_definition_by_department(self, source_path):
        definition = None
        print("dept: ", self.department)

        if self.department == Department.MATERIAL:
            definition = hou.hdaDefinition(hou.sopNodeTypeCategory(), "dcc_material", source_path)
        elif self.department == Department.MODIFY:
            definition = hou.hdaDefinition(hou.sopNodeTypeCategory(), "dcc_modify", source_path)
        elif self.department == Department.HAIR:
            definition = hou.hdaDefinition(hou.objNodeTypeCategory(), "dcc_hair", source_path)
        elif self.department == Department.CLOTH:
            definition = hou.hdaDefinition(hou.objNodeTypeCategory(), "dcc_cloth", source_path)


        return definition

    def publish_selection_results(self, value):

        selected_publish = None
        for item in self.sanitized_publish_list:
            if value[0] == item:
                selected_publish = item

        selected_file = None
        for publish in self.publishes:
            label = publish[0] + " " + publish[1] + " " + publish[2]
            if label == selected_publish:
                selected_file = publish[3]

        print("selected file: ", selected_file)

        definitions = hou.hda.definitionsInFile(selected_file)
        definition = definitions[0]

        parent = self.node.parent()
        print("node: ", self.node, str(self.node))
        type = self.node.type().name()
        print("type: ", str(type))
        self.node.destroy()

        # source_path = self.node.type().sourcePath()
        # print("source path: ", source_path)
        hou.hda.installFile(selected_file)
        hou.hda.reloadFile(selected_file)
        # definition = self.get_definition_by_department(selected_file)

        print("def: ", definition)
        definition.setPreferred(True)

        new_node = parent.createNode(str(type), node_name=self.department)
        print("new node: ", new_node)
        new_node.allowEditingOfContents()

        geo = parent.node("geo")
        if geo is None:
            qd.error("There should be a geo network. Something went wrong, so you'll need to place the node manually.")
            parent.layoutChildren()
            return

        if self.department == Department.HAIR or self.department == Department.CLOTH:
            new_node.setInput(0, geo)

        elif self.department == Department.MODIFY:
            # If there is a material node, put the modify node in between material and geo.
            material = parent.node("material")
            if material is not None:
                new_node.setInput(0, geo)
                material.setInput(0, new_node)
            else:  # Else, stick it between geo and shot_modeling.
                new_node.setInput(0, geo)
                shot_modeling.setInput(0, new_node)

        elif self.department == Department.MATERIAL:
            # If there is a modify node, put the material node in between modify and shot_modeling.
            modify = parent.node("modify")
            if modify is not None:
                new_node.setInput(0, modify)
                shot_modeling.setInput(0, new_node)
            else:  # Else, stick it between geo and shot_modeling.
                new_node.setInput(0, geo)
                shot_modeling.setInput(0, new_node)

        parent.layoutChildren()

    def rollback_asset(self, node=None):
        pass

    def rollback_tool(self, node=None):
        pass

    def rollback_shot(self):
        pass
