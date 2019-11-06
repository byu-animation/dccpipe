import os
import nuke

from pipe.am.project import Project
from pipe.am.environment import Department
from pipe.am.environment import Environment
import pipe.gui.select_from_list as sfl
import pipe.gui.quick_dialogs as qd
from pipe.tools.nuketools.nukeutils import utils


class TemplateCreator:

    def __init__(self):
        pass

    def create_from_current(self):
        script_name = qd.input("Enter a name for this template: ")
        if not script_name or script_name == u'':
            return
            
        templates_dir = Environment().get_templates_dir()
        temp_filepath = os.path.join(templates_dir, script_name + ".nk")
        basename = os.path.basename(temp_filepath)

        templates_in_dir = os.listdir(templates_dir)
        print("templates: ", templates_in_dir)
        if basename in templates_in_dir:
            overwrite = qd.yes_or_no(str(script_name) + " already exists. Overwrite it?")

            if overwrite:
                nuke.scriptSave(temp_filepath)
                qd.info("Template created successfully!")
        else:
            nuke.scriptSave(temp_filepath)
            qd.info("Template created successfully!")

        print("filepath: ", temp_filepath)
