import os
import json

def read_project_settings():
    with open(".settings", "r") as jsonFile:
        data = json.load(jsonFile)

    return data

def set_environment_vars(data):
    hou_path = str(data['hou_launch_path'])
    maya_path = str(data['maya_launch_path'])
    nuke_path = str(data['nuke_launch_path'])
    sbs_path = str(data['sbs_launch_path'])

    os.environ["DCC_HOUDINI_LAUNCH_PATH"] = hou_path;
    os.environ["DCC_MAYA_LAUNCH_PATH"] = maya_path;
    os.environ["DCC_NUKE_LAUNCH_PATH"] = nuke_path;
    os.environ["DCC_SBS_LAUNCH_PATH"] = sbs_path;
    print(os.environ)
    # print("here")

set_environment_vars(read_project_settings())
# print("done")
