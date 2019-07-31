import pipe.gui.quick_dialogs as qd
import pipe.gui.select_from_list as sfl
from pipe.am.project import Project
from pipe.am.environment import Environment
from pipe.am.body import Body
from pipe.am.body import AssetType
from pipe.tools.mayatools.utils.utils import *
from PySide2 import QtWidgets


'''
Parent class for managing assets
'''

class Creator:

    def __init__(self):
        self.name = None

    '''
    This will bring up the create new body UI
    '''
    def create_body(self):
        self.name = qd.input("What's the name of this asset?")

        if self.name is None:
            return

        asset_type_list = AssetType().list_asset_types()

        self.item_gui = sfl.SelectFromList(l=asset_type_list, parent=maya_main_window(), title="What are you creating?", width=250, height=120)
        self.item_gui.submitted.connect(self.results)

    def results(self, value):
        print("Final value: ", value[0])
        type = value[0]
        name = self.name

        # determine if asset was created or not.
        created = True

        if name is None or type is None:
            created = False

        if created:
            project = Project()
            body = project.create_asset(name, asset_type=type)
            if body == None:
                # print a message about failure/duplicate
                qd.error("Asset not found, publish failed.")
            else:
                prepare_scene_file()
                # show the gui, get the element. To list elements, get the body and get the department
                department = "model"  # hard-coding model for now since this is Maya
                asset_list = body.list_elements(department)

                # get the element for the model dept and the user, and using that publish
                selected_element = body.get_element("modify")

                user = Environment().get_user()
                post_publish(selected_element, user, published=True, comment="First commit.")  # FIXME: WE NEED TO FIGURE OUT TO WHICH DEPARTMENT(S) WE ACTUALLY NEED TO PUBLISH TO

                selected_element = body.get_element("model")
                post_publish(selected_element, user, published=True, comment="First commit.")

                qd.info("Asset created successfully (but not really, yet).", "Success")

        else:
            qd.error("Asset creation failed.")
