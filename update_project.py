import pipe.am.pipeline_io as pipeline_io
import os
import json
import subprocess
import argparse


'''
Script used to determine what aspects of dccpipe to update
'''
def get_arguments_and_run():
    parser = argparse.ArgumentParser(description='Usage: python update_project.py --shortcuts --name myName --nickname myNick --email myEmail')
    parser.add_argument("--shortcuts", "-sc", action="store_true", help="If present, shortcuts will be regenerated.")
    parser.add_argument("--name", "-n", type=str, help="If present, update the name of the Project in the .project file with the specified value.")
    parser.add_argument("--nickname", "-nn", type=str, help="If present, update the nickname of the Project in the .project file with the specified value.")
    parser.add_argument("--email", "-e", type=str, help="If present, update the email of the Project in the .project file with the specified value.")

    args = parser.parse_args()
    shortcuts = args.shortcuts
    name = args.name
    nickname = args.nickname
    email = args.email

    if shortcuts == False and name == None and nickname == None and email == None:
        print('Usage: python update_project.py --shortcuts --name myName --nickname myNick --email myEmail')
        return

    if name:
        modify_project_config("name", name)
    if nickname:
        modify_project_config("nickname", nickname)
    if email:
        modify_project_config("email_address", email)
    if shortcuts:
        create_project_shortcuts()

    print("Production project successfully updated!")

def modify_project_config(key, value):
        with open(".project", "r") as jsonFile:
            data = json.load(jsonFile)

        data[key] = value

        with open(".project", "w") as jsonFile:
            json.dump(data, jsonFile)

def create_project_shortcuts():
    pipe_dict = pipeline_io.readfile(".project")
    nickname = pipe_dict['nickname']
    name = pipe_dict['name']

    cwd = os.getcwd()
    icon_script = os.path.join(cwd, 'create_project_shortcuts.sh')

    if nickname is not None or nickname is not "":
        subprocess.call(['sh', icon_script, '-n', nickname, name, cwd])
    else:
        subprocess.call(['sh', icon_script, name, cwd])

get_arguments_and_run()
