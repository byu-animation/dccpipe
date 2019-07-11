import pipe.gui.quick_dialogs as qd
import pipe.gui.select_from_list as sfl
from pipe.am.project import Project
from pipe.am.environment import Environment
from pipe.am.body import Body
from pipe.am.mayatools.utils.utils import *


'''
Parent class for managing assets
'''

class Creator():

    def __init__(self):
        pass

    '''
    This will bring up the create new body UI
    '''
    def create_body(self):
        name = qd.input("What's the name of this asset?")
        type = qd.input("What's the type?")

        # determine if asset was created or not.
        created = True

        if name is None or type is None:
            created = False

        if created:
            project = Project()
            body = project.create_asset(name, asset_type=type)
            if body == None:
                # print a message about failure/duplicate
                qd.error("Body not found, publish failed.")
            else:
                # correct so far
                # TODO: publish
                prepare_scene_file()
                # show the gui, get the element. To list elements, get the body and get the department
                department = "model"  # hard-coding model for now since this is Maya
                asset_list = body.list_elements(department)
        		self.item_gui = sfl.SelectFromList(l=asset_list, parent=maya_main_window(), title="Select an asset to publish to")
        		self.item_gui.submitted.connect(self.results)
        else:
            qd.error("Asset creation failed.")


	def results(self, value):
		print("Final value: ", value[0])
		filename = value[0]

		project = Project()
		body = project.get_body(filename)

		# get the element for the model dept and the user, and using that publish
		selected_element = body.get_element("model")

        user = Environment().get_user()
        post_publish(selected_element, user, published=True, comment="No comment.")

        qd.info("Asset created successfully (but not really, yet).", "Success")
