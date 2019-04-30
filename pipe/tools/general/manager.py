import pipe.gui.quick_dialogs as qd


'''
Parent class for managing assets
'''

class Manager():

    def __init__(self):
        pass

    '''
    This will bring up the create new body UI
    '''
    def create_body(self):
        name = qd.input("What's the name of this asset?")

        # determine if asset was created or not.
        created = True

        if created:
            qd.info("Asset created successfully (but not really, yet).")
        else:
            qd.error("Asset creation failed.")
