import pymel.core as pm
from pipe.gui.quick_dialogs import yes_or_no
from pipe.gui.quick_dialogs import message as message_gui
from pipe.tools.mayatools.utils.utils import *


class centerOrigin():

    def go(self):
        #result = yes_or_no('Is there ONLY ONE prop in the scene?')
        #if result:
        center_object_at_origin()
        #else:
        #save_scene_file()
    	  # message_gui('No objects were centered')
