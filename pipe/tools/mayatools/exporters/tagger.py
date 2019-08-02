from pymel.core import *
from pipe.gui import quick_dialogs as qd
from pipe.tools.mayatools.utils.utils import *


class Tagger:
    def __init__(self):
        pass

    def tag(self):
        selected = ls(sl=True, tr=True)

        response = qd.binary_option("Add Alembic tag to:\n" + str(selected_groups), "Yes", "No", title='Add Alembic Tag')

        if response:
            for node in selected:
                tag_node_with_flag(node, "DCC_Alembic_Export_Flag")

            qd.info("tag successful!")

    def untag(self):
        selected = ls(sl=True, tr=True)

        response = qd.binary_option("Add Alembic tag to:\n" + str(selected_groups), "Yes", "No", title='Add Alembic Tag')

        if response:
            for node in selected:
                untag_node_with_flag(node, "DCC_Alembic_Export_Flag")

            qd.info("tag successful!")
