import os

# Other export scripts
from pipe.tools.mayatools.utils.utils import *
from pipe.am.environment import Environment
from pipe.am.body import Body
from pipe.am.project import Project
import pipe.gui.quick_dialogs as qd


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

    def __init__(self, gui=True, src=None, quick_publish=False):
        self.quick_publish = quick_publish

    def fast_publish(self):
        asset_name = os.environ.get("DCC_ASSET_NAME")
        department = os.environ.get("DCC_DEPARTMENT")
        self.non_gui_publish(asset_name, department)

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

        asset_type = self.body.get_type()
        department_list = get_departments_by_type(asset_type)

        self.item_gui = sfl.SelectFromList(l=department_list, parent=maya_main_window(), title="Select department for this publish")
        self.item_gui.submitted.connect(self.department_results)

    def department_results(self, value):
        chosen_department = value[0]

        prepare_scene_file(quick_publish=self.quick_publish)

        print("value: ", value)
        print("dept: ", chosen_department)

        # get the element for the model dept and the user, and using that publish
        selected_element = self.body.get_element(chosen_department)
        user = Environment().get_user()

        # get the comment
        comment = qd.input("Comment for publish")
        if comment is None:
            comment = "No comment."

        setPublishEnvVar(self.body.get_name(), chosen_department)
        post_publish(selected_element, user, published=True, comment=comment)

        qd.info("Asset published successfully.", "Success")

    def non_gui_publish(self, asset_name, department):
        project = Project()
        self.body = project.get_body(asset_name)

        self.department_results([department])
