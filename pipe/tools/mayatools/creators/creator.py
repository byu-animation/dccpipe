import pipe.gui.quick_dialogs as qd
from pipe.am.project import Project


'''
Parent class for managing assets
'''

class Creator():

    def __init__(self):
        pass

    '''
    This will bring up the create new body UI
    '''
    def create_body(self):
        name = qd.input("What's the name of this asset?")
        type = qd.input("What's the type?")

        # determine if asset was created or not.
        created = True

        if name is None or type is None:
            created = False

        if created:
            project = Project()
            project.create_asset(name, asset_type=type)
            # TODO: something's not quite right here, as the .mb file is not created or saved. Also there should be an intitial commit.
            qd.info("Asset created successfully (but not really, yet).", "Success")
        else:
            qd.error("Asset creation failed.")
