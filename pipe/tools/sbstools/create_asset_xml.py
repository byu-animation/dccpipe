import os
import sys
import subprocess
from pipe.am.project import Project
from pipe.am.environment import Environment


def create_asset_xml():
    project = Project()
    asset_list = project.list_props_and_actors()
    filename = os.path.join(Environment().get_project_dir(), "assets.xml")

    open(filename, "w").close()  # wipe the file
    f = open(filename, "a")  # open the file for appending
    write_to_file("<channel>\n")

    for asset in asset_list:
        text = "\t<item>" + str(asset) + "</item>\n"
        write_to_file(f, filename, text)

    write_to_file("</channel>\n")
    f.close()

def write_to_file(file, filename, text):
    f.write(text)
