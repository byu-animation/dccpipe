import pymel.core as pm
from pipe.gui.quick_dialogs import yes_or_no
from pipe.gui.quick_dialogs import message as message_gui
from pipe.tools.mayatools.utils.utils import *


class resetPosition():

    def go(self):
        #result = yes_or_no('Is there ONLY ONE prop in the scene?')
        #if result:
        reposition_object_to_old_pos()
        #else:
        #save_scene_file()
    	  # message_gui('No objects were centered')
