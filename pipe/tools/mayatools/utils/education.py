import pymel.core as pm
from pipe.gui.quick_dialogs import message as message_gui
from pipe.tools.mayatools.utils.utils import *


class education():

    def go(self):
        convert_to_education()
        save_scene_file()
    	message_gui('This Maya file has been converted to an education licence')
