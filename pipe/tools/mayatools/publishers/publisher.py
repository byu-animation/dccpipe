import os

# Other export scripts
from pipe.tools.mayatools.utils.utils import *
from pipe.am.environment import Environment
from pipe.am.body import Body
from pipe.am.project import Project


from pipe.gui.checkbox_options import CheckBoxOptions
import pipe.gui.select_from_list as sfl

try:
    from PySide.QtCore import Slot
except ImportError:
    from PySide2.QtCore import Slot


'''
    Works as a publisher, but adds an additional scene prep dialog at the beginning,
    and runs the Maya export scripts at the end.
'''
class MayaPublisher:

    def __init__(self, gui=True, src=None):
        pass

    def publish(self):
        # this is the function that we will use to publish.

        project = Project()

        asset_list = project.list_assets()

        self.item_gui = sfl.SelectFromList(l=asset_list, parent=maya_main_window(), title="Select an asset to publish to")
        self.item_gui.submitted.connect(self.asset_results)

    def asset_results(self, value):
        chosen_asset = value[0]

        project = Project()
        self.body = project.get_body(chosen_asset)

        department_list = self.body.default_departments()

        self.item_gui = sfl.SelectFromList(l=department_list, parent=maya_main_window(), title="Select department for this publish")
        self.item_gui.submitted.connect(self.department_results)

        # TODO: get the body, get the department.
        # body = project.create_asset(name, asset_type=type)
        # selected_element = body.get_element("model")
        # department = "model"

        # TODO: publish
        # show the gui, get the element. To list elements, get the body and get the department


    def department_results(self, value):
        chosen_department = value[0]

        prepare_scene_file()

        project = Project()
        body = project.get_body(filename)

        # get the element for the model dept and the user, and using that publish
        selected_element = body.get_element("model")

        user = Environment().get_user()
        post_publish(selected_element, user, published=True, comment="No comment.")

        qd.info("Asset created successfully (but not really, yet).", "Success")

#TODO: FIXME. LOTS OF STUFF TO DO PRIOR TO PUBLISHING FROM MAYA. ALL THE FOLLOWING.

    def go():
    	parent = maya_main_window()
    	filePath = cmds.file(q=True, sceneName=True)
    	if not filePath:
    		filePath = Environment().get_user_workspace()
    		filePath = os.path.join(filePath, 'untitled.mb')
    		filePath = pipeline_io.version_file(filePath)
    		cmds.file(rename=filePath)
    		cmds.file(save=True)
    	global maya_publish_dialog
    	maya_publish_dialog = PublishWindow(filePath, parent, [Department.MODEL, Department.RIG, Department.LAYOUT, Department.ANIM, Department.CFX, Department.CYCLES])
    	maya_publish_dialog.finished.connect(post_publish)

    # TODO: SET UP A FUNCTION FOR PUBLISH WITHOUT GUI
    # def non_gui_publish(element, user, src, comment):
    # 	dst = element.publish(user, src, comment)
    # 	#Ensure file has correct permissions
    # 	try:
    # 		os.chmod(dst, 0660)
    # 	except:
    # 		pass
    #
    # 	# TODO: export playblast
    #
    #     print element.get_name()
