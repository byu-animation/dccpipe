import pipe.am.pipeline_io as pipeline_io
import os
import sys
import json
import subprocess


project_dict = {"reference_dir": "production/reference_geo/",
     "name": "TestProject",
     "assets_dir": "production/assets/",
     "users_dir": "production/users/",
     "nickname": "test",
     "crowds_dir": "production/crowds/",
     "tools_dir": "production/tools/",
     "templates_dir": "production/templates/",
     "shots_dir": "production/rendered_shots/",
     "email_address": "a@b.com",
     "hda_dir": "production/hdas/",
     "email_password": "password",
     "production_dir": "production/"}


'''
Python script to initialize the production side of the pipe.
Usage - python create_project.py nameOfProject nicknameOfProject
'''
def create_project():
    if not len(sys.argv) == 3:
        print("Create project failed. Invalid number of arguments.")
        print("Usage - python create_project.py nameOfProject nicknameOfProject")
        return
    project_dir = os.getenv("MEDIA_PROJECT_DIR")

    # get the command line arguments 1 - name, 2 - nickname
    name = sys.argv[1]
    nickname = sys.argv[2]
    create_project_config()
    modify_project_config(name, nickname)

    pipe_dict = pipeline_io.readfile(".project")

    pipeline_io.mkdir(pipe_dict["production_dir"])
    pipeline_io.mkdir(pipe_dict["assets_dir"])
    pipeline_io.mkdir(pipe_dict["crowds_dir"])
    pipeline_io.mkdir(pipe_dict["shots_dir"])
    pipeline_io.mkdir(pipe_dict["tools_dir"])
    pipeline_io.mkdir(pipe_dict["users_dir"])
    pipeline_io.mkdir(pipe_dict["hda_dir"])
    pipeline_io.mkdir(pipe_dict["reference_dir"])

    create_project_shortcuts(nickname=nickname, name=name)

    print("Production project successfully created!")

def create_project_config():
    with open(".project", "w") as jsonFile:
        json.dump(project_dict, jsonFile)


def modify_project_config(name, nickname):
    with open(".project", "r") as jsonFile:
        data = json.load(jsonFile)

    # tmp = data["name"]
    data["name"] = name
    data["nickname"] = nickname

    with open(".project", "w") as jsonFile:
        json.dump(data, jsonFile)

def create_project_shortcuts(nickname="test", name="test"):
    cwd = os.getcwd()
    icon_script = os.path.join(cwd, 'create_project_shortcuts.sh')

    if(nickname is not None):
        subprocess.call(['sh', icon_script, '-n', nickname, name, cwd])
    else:
        subprocess.call(['sh', icon_script, name, cwd])

create_project()
