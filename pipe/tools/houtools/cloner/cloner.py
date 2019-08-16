import hou
import os
# from PySide2 import QtGui, QtWidgets, QtCore
import pipe.gui.quick_dialogs as qd
import pipe.gui.select_from_list as sfl

from pipe.tools.houtools.utils.utils import *

from pipe.am.project import Project
from pipe.am.body import Body
from pipe.am.element import Element
from pipe.am.environment import Department
from pipe.am.environment import Environment


class Cloner:

    def __init__(self):
        self.item_gui = None
        self.modify_publish = None
        self.material_publish = None
        self.hair_publish = None
        self.cloth_publish = None
        environment = Environment()
        self.user = environment.get_user()

    def clone_shot():
        filepath = self.hou_clone_dialog.result
        if filepath is not None:
            if not os.path.exists(filepath):
                print('Filepath doesn\'t exist')
                filepath += '.hipnc'
                hou.hipFile.clear()
                hou.hipFile.setName(filepath)
                hou.hipFile.save()
            else:
                hou.hipFile.load(filepath)

    def clone_asset(self, node=None):
        self.clone_hda(hda=node)

    def clone_tool(self, node=None):
        self.clone_hda(hda=node)

    def clone_shot(self):
        project = Project()
        environment = Environment()

        self.hou_clone_dialog = cloneWindow(houdini_main_window(), [Department.LIGHTING, Department.FX])
        hou_clone_dialog.finished.connect(clone_shot)

    def clone_hda(self, hda=None):
        project = Project()

        asset_list = project.list_assets()
        self.item_gui = sfl.SelectFromList(l=asset_list, parent=houdini_main_window(), title="Select an asset to clone")
        self.item_gui.submitted.connect(self.asset_results)

    def asset_results(self, value):
        print("Selected asset: ", value[0])
        filename = value[0]

        project = Project()
        self.body = project.get_body(filename)

        self.modify_element = self.body.get_element("modify")
        self.material_element = self.body.get_element("material")
        self.hair_element = self.body.get_element("hair")
        self.cloth_element = self.body.get_element("cloth")

        self.filepath = self.body.get_filepath()

        modify_publish = self.modify_element.get_last_publish()
        material_publish = self.material_element.get_last_publish()
        hair_publish = self.hair_element.get_last_publish()
        cloth_publish = self.cloth_element.get_last_publish()

        if not modify_publish and not material_publish and not hair_publish and not cloth_publish:
            department_paths = None
        else:
            department_paths = {}

        if(modify_publish):
            self.modify_publish = modify_publish[3]
            department_paths['modify'] = self.modify_publish
        if(material_publish):
            self.material_publish = material_publish[3]
            department_paths['material'] = self.material_publish
        if(hair_publish):
            self.hair_publish = hair_publish[3]
            department_paths['hair'] = self.hair_publish
        if(cloth_publish):
            self.cloth_publish = cloth_publish[3]
            department_paths['cloth'] = self.cloth_publish

        from pipe.tools.houtools.assembler.assembler import Assembler  # put import here to remove cross import issue FIXME
        node, created_instances =  Assembler().create_hda(filename, body=self.body, department_paths=department_paths)
        layout_object_level_nodes()

        return node, created_instances
