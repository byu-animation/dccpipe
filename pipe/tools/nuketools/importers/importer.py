import os
import nuke

from pipe.am.project import Project
from pipe.am.environment import Department
from pipe.am.environment import Environment
import pipe.gui.select_from_list as sfl
from pipe.tools.nuketools.nukeutils import utils


class NukeImporter:

    def __init__(self):
        pass

    def import_shot(self):
        shots = Project().list_shots()

        self.item_gui = sfl.SelectFromList(l=shots, parent=utils.get_main_window(), title="Select a shot to import:")
        self.item_gui.submitted.connect(self.results)

    def shot_results(self, values):
        selection = str(values[0])

        shot = Project().get_body(selection)
        render_element = shot.get_element(Department.RENDER)
        render_filepath = str(render_element.get_dir()) + '/'

        read = nuke.createNode("Read", "file " + str(render_filepath))

        comp_element = shot.get_element(Department.COMP)
        comp_filepath = str(comp_element.get_cache_dir())
        comp_filepath = os.path.join(comp_filepath, selection + ".####.jpg")
        write = nuke.createNode("Write", "file " + comp_filepath)

    def import_template(self):
        self.templates_dir = Environment().get_templates_dir()
        files = os.listdir(self.templates_dir)

        self.item_gui = sfl.SelectFromList(l=files, parent=utils.get_main_window(), title="Select template(s) to import", multiple_selection=True)
        self.item_gui.submitted.connect(self.template_results)

    def template_results(self, files):
        for file in files:
            try:
                path = os.path.join(self.templates_dir, file)
                name, ext = os.path.splitext(file)
                nuke.nodePaste(path)

            except Exception as e:
                qd.warning(str(e))
