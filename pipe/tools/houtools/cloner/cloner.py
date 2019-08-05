import *  # Something
from __future__ import print_function
# Author: Trevor Barrus
import hou
import os
from PySide2 import QtGui, QtWidgets, QtCore
from pipe.gui.checkout_gui import CheckoutWindow
from pipe.gui.quick_dialogs import quick_dialogs as qd

from pipe.am.project import Project
from pipe.am.body import Body
from pipe.am.element import Element
from pipe.am.environment import Department

class Cloner:

    def __init__(self):
		self.hou_checkout_dialog = None

    def checkout_shot():
        filepath = self.hou_checkout_dialog.result
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
        self.checkout_hda_go(hda=node)

    def clone_tool(self, node=None):
        self.checkout_hda_go(hda=node)

    def clone_shot(self):
        project = Project()
        environment = Environment()

        self.hou_checkout_dialog = CheckoutWindow(hou.ui.mainQtWindow(), [Department.LIGHTING, Department.FX])
        hou_checkout_dialog.finished.connect(checkout_shot)

    def checkout_hda_go(self, hda=None):
        #self.checkout_window
        project = Project()
        environment = Environment()
        if hda is None:
            nodes = hou.selectedNodes()
            if len(nodes) == 1:
                hda = nodes[0]
            elif len(nodes) > 1:
                qd.error('Only one node can be selected for checkout')
                return
            else:
                qd.error('You need to select an asset node to checkout')
                return

        if hda.type().definition() is not None:
            result = self.checkout_hda(hda, project, environment)
            if result is not None:
                print('checkout successful')
                #I think having the node unlock is visual que enough that the checkout was fine. Mostly it's annoying to have the window there. And we have a window that will let them know if it didn't work.
                #qd.info('Checkout Successful!', title='Success!')
            else:
                qd.error('Checkout Failed', title='Failure :()')
            else:
                qd.error('Node is not a digital asset')
                return

    def checkout_hda(self, hda, project, environment):
        '''
        hda - an hda to checkout
        Returns the element_path if the checkout was successful. Otherwise return None
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
                qd.error('We could not find ' + asset_name + ' in the list of things you can checkout.')

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
                    element_path = element.checkout(current_user)
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
