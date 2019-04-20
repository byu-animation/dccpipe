import os

# Other export scripts
import hou #need houdini here PLS FIX

# We're going to need asset management module
from byuam import Environment, Project

# Minimal UI
from byuminigui.checkbox_options import CheckBoxOptions
from byuminigui.select_from_list import SelectFromList

# Import BYU Tools
from byutools.publisher import Publisher

try:
    from PySide.QtCore import Slot
except ImportError:
    from PySide2.QtCore import Slot


'''
    Works as a publisher, but adds an additional scene prep dialog at the beginning,
    and runs the Maya export scripts at the end.
'''
class HoudiniPublisher(Publisher):
