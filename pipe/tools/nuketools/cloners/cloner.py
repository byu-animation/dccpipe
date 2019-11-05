import os
import nuke

from pipe.am.project import Project
from pipe.am.environment import Department
from pipe.am.environment import Environment
import pipe.gui.select_from_list as sfl
import pipe.gui.quick_dialogs as qd
from pipe.tools.nuketools.nukeutils import utils
from pipe.tools.nuketools.importers import importer


class NukeCloner:

    def __init__(self):
        pass

    def clone(self):
        shots = Project().list_shots()

        self.item_gui = sfl.SelectFromList(l=shots, parent=utils.get_main_window(), title="Select a shot to clone/import:")
        self.item_gui.submitted.connect(self.results)

    def results(self, values):
        selection = str(values[0])

        shot = Project().get_body(selection)
        comp_element = shot.get_element(Department.COMP)
        self.publishes = comp_element.list_publishes();

        os.environ["DCC_NUKE_ASSET_NAME"] = selection;
        if not self.publishes:
            # has not been imported. Import it first.
            shot_importer = importer.NukeImporter()
            shot_importer.shot_results([selection])
            return
        else:
            # get the latest publish
            username = Environment().get_current_username()
            filepath = comp_element.checkout(username)

            if os.path.exists(filepath):
                nuke.scriptOpen(filepath)
            else:
                qd.error("Couldn't find the file.")
