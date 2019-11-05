import os
import nuke

from pipe.am.project import Project
from pipe.am.environment import Department
from pipe.am.environment import Environment
import pipe.gui.select_from_list as sfl
import pipe.gui.quick_dialogs as qd
from pipe.tools.nuketools.nukeutils import utils


class NukePublisher:

    def __init__(self):
        pass

    def publish(self, quick=True):
        if quick:
            shot_name = os.environ.get("DCC_NUKE_ASSET_NAME")
        else:
            shot_name = None

        if shot_name is None:
            shots = Project().list_shots()
            self.item_gui = sfl.SelectFromList(l=shots, parent=utils.get_main_window(), title="Select a shot to publish to:")
            self.item_gui.submitted.connect(self.results)

        else:
            self.results([shot_name])

    def results(self, values):
        shot_name = str(values[0])
        shot = Project().get_body(shot_name)
        comp_element = shot.get_element(Department.COMP)

        user_workspace = Environment().get_user_workspace()
        temp_filepath = os.path.join(user_workspace, shot_name + ".nk")
        # filepath = nuke.toNode("root").name() #grab name of file they're working on
        nuke.scriptSave(temp_filepath)

        print("filepath: ", temp_filepath)

        user = Environment().get_current_username()
        comment = qd.input("Comment for publish")
        if comment is None:
            comment = "Publish by " + str(user) + " in comp."

        comp_element.publish(user, temp_filepath, comment)

        os.environ["DCC_NUKE_ASSET_NAME"] = shot_name;
