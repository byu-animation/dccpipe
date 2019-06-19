import os
import sys
import json

def update_key_value(filepath, **kwargs):
    with open(filepath, "r") as json_file:
        data = json.load(json_file)

    data.update(**kwargs)

    with open(filepath, "w") as json_file:
        json.dump(data, json_file)

def get_key_value(filepath, key):
    with open(filepath, "r") as json_file:
        data = json.load(json_file)
        return data[key]

def set_project_name(projectfile, name):
    data = { "name" : name }
    update_key_value(projectfile, data)

def set_project_nickname(projectfile, nickname):
    data = { "nickname" : nickname }
    update_key_value(projectfile, data)

def add_department(projectfile, new_department):
    current_departments = get_key_value(projectfile, "departments")
    if department in current_departments:
        if new_department.name == department["name"]:
            print "Department already exists"
            return False
    else:
        current_departments.append(department.as_dict())
        data = { "departments" : current_departments }
        update_key_value(projectfile, data)
        print "Added {}".format(project_file)
        return True

def update_department(projectfile, updated_department):
    current_departments = get_key_value(projectfile, "departments")
    match = [ x for x in current_departments if x["name"] == updated_department.name ]
    if len(match) < 1:
        print "Department does not exist"
        return False
