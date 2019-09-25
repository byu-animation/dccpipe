import pipe.gui.quick_dialogs as qd
import pipe.gui.select_from_list as sfl
from pipe.am.project import Project
from pipe.am.environment import Environment
from pipe.am.body import Body
from pipe.am.body import AssetType
from pipe.am import pipeline_io
from pipe.tools.mayatools.utils.utils import *
import re
from PySide2 import QtWidgets


'''
    Maya class for creating new assets
'''
class Creator:

    def __init__(self):
        self.name = None
        self.export = False

    def create_body_and_export(self):
        self.export = True
        self.create_body()

    '''
    This will bring up the create new body UI
    '''
    def create_body(self):
        self.name = qd.input("What's the name of this asset?")

        if self.name is None:
            return

        #Error checking
        name = str(self.name)
        if not pipeline_io.checkFileName(name):
            self.create_body()
            return
        asset_type_list = AssetType().list_maya_types()

        self.item_gui = sfl.SelectFromList(l=asset_type_list, parent=maya_main_window(), title="What are you creating?", width=250, height=120)
        self.item_gui.submitted.connect(self.results)

    def results(self, value):
        type = value[0]
        name = self.name

        # determine if asset was created or not.
        created = True

        if name is None or type is None:
            created = False

        if created:
            scene_file, new_file = get_scene_file()
            print("scene file, new file: ", scene_file, new_file)
            check_unsaved_changes()
            project = Project()
            body = project.create_asset(name, asset_type=type)

            if body == None:
                # print a message about failure/duplicate
                qd.error("Asset with name " + str(name) + " already exists in pipeline.")
            else:
                prepare_scene_file(body=body)
                department = "model"
                asset_list = body.list_elements(department)

                selected_element = body.get_element(department)
                user = Environment().get_user()

                print("name :", str(name))
                print("department: ", department)
                setPublishEnvVar(name, department);
                post_publish(selected_element, user, self.export, published=True, comment="First publish!")

                qd.info("Asset created successfully!", "Success")

        else:
            qd.error("Asset creation failed.")
