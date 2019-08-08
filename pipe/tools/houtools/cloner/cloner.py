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

from pipe.tools.houtools.assembler.assembler import Assembler

class Cloner:

    def __init__(self):
        self.item_gui = None
        self.modify_publish = None
        self.material_publish = None
        self.hair_publish = None
        self.cloth_publish = None

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
        self.clone_hda_go(hda=node)

    def clone_tool(self, node=None):
        self.clone_hda_go(hda=node)

    def clone_shot(self):
        project = Project()
        environment = Environment()

        self.hou_clone_dialog = cloneWindow(houdini_main_window(), [Department.LIGHTING, Department.FX])
        hou_clone_dialog.finished.connect(clone_shot)

    def clone_hda_go(self, hda=None):
        #self.clone_window
        project = Project()
        environment = Environment()
        self.user = environment.get_user()

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

        if(modify_publish):
            self.modify_publish = modify_publish[3]
            print("modify :", self.modify_publish)
        if(material_publish):
            self.material_publish = material_publish[3]
        if(hair_publish):
            self.hair_publish = hair_publish[3]
        if(cloth_publish):
            self.cloth_publish = cloth_publish[3]
            print("cloth :", self.cloth_publish)

        department_paths = []

        #Assembler.create_hda_attack_of_the_cloner()
            # hda = hou.createNode(selected_scene_file)
            # print("hda: ", hda)

            # definition = hou.hdaDefinition(hda.type().category(), hda.type().name(), element_path)
            # definition.setPreferred(True)
            # #hou.hda.uninstallFile(src, change_oplibraries_file=False)
            # hda.allowEditingOfContents()

            # bring in the hda

        # if hda is None:
        #     nodes = hou.selectedNodes()
        #     if len(nodes) == 1:
        #         hda = nodes[0]
        #     elif len(nodes) > 1:
        #         qd.error('Only one node can be selected for clone')
        #         return
        #     else:
        #         qd.error('You need to select an asset node to clone')
        #         return
        #
        # if hda.type().definition() is not None:
        #     result = self.clone_hda(hda, project, environment)
        #     if result is not None:
        #         print('clone successful')
        #         #I think having the node unlock is visual que enough that the clone was fine. Mostly it's annoying to have the window there. And we have a window that will let them know if it didn't work.
        #         #qd.info('clone Successful!', title='Success!')
        #     else:
        #         qd.error('clone Failed', title='Failure :()')
        # else:
        #     qd.error('Node is not a digital asset')
        #     return

    def clone_hda(self, hda, project, environment):
        '''
        hda - an hda to clone
        Returns the element_path if the clone was successful. Otherwise return None
        '''
        #if node is digital asset
        if hda.type().definition() is not None:
            asset_name = hda.type().name() #get name of hda
            index = asset_name.rfind('_')
            department_name = asset_name[index+1:]
            # Our old assets have "_main" at the end. We want them to refer to the "assembly" department.
            department_name = "assembly" if department_name == "main" else department_name
            asset_name = asset_name[:index]
            src = hda.type().definition().libraryFilePath()
            current_user = environment.get_current_username()

            if asset_name in project.list_assets():
                body = project.get_asset(asset_name)
            elif asset_name in project.list_tools():
                body = project.get_tool(asset_name)
            else:
                qd.error('We could not find ' + asset_name + ' in the list of things you can clone.')

            if department_name not in Department.ALL:
                qd.error(department_name + ' is not a valid Department')
                return None

            if os.path.exists(src):
                if body is not None:
                    if Element.DEFAULT_NAME in body.list_elements(department_name):
                        element = body.get_element(department_name, Element.DEFAULT_NAME)
                    elif Element.DEFAULT_NAME in body.list_elements(Department.HDA):
                        element = body.get_element(Department.HDA, Element.DEFAULT_NAME)
                    else:
                        qd.error('There was a problem checking out the selected hda', details='The body for this HDA could not be found. This seems weird because we were able to find the asset_name in the list of assets. Right off the top of my head I don\'t know why it would do this. We\'ll have to take closer look.')
                        return None
                    element_path = element.clone(current_user)
                    hou.hda.installFile(element_path)
                    definition = hou.hdaDefinition(hda.type().category(), hda.type().name(), element_path)
                    definition.setPreferred(True)
                    #hou.hda.uninstallFile(src, change_oplibraries_file=False)
                    hda.allowEditingOfContents()
                    aa = hda.parm("ri_auto_archive")
                    if aa:
                        aa.set("force")
                    return element_path
            return None
