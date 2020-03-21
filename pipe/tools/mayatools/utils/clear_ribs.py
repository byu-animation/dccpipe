from pipe.am.project import Project
from pipe.tools.mayatools.utils.utils import *
import pipe.gui.select_from_list as sfl


class ClearRibs:

    def __init__(self):
        pass

    def go(self):
        project = Project()
        asset_list = project.list_shots()
        self.item_gui = sfl.SelectFromList(l=asset_list, parent=maya_main_window(), title="Select shots to clear Ribs/IFDs", multiple_selection=True)
        self.item_gui.submitted.connect(self.results)

    def results(self, values):
        Project().delete_ribs_for_bodies(values)
