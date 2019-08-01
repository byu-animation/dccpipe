from pymel.core import *
from pipe.gui import quick_dialogs as qd


class Tagger:
    def __init__(self):
        pass

    def tag(self):
        self.tagGeo()

    def tagGeo(self):
        selected_groups = ls(sl=True, tr=True)

        response = qd.binary_option("Add Alembic tag to:\n" + str(selected_groups), "Yes", "No", title='Add Alembic Tag')

        if response:
            for obj in selected_groups:
                if not obj.hasAttr("DCC_Alembic_Export_Flag"):
                    cmds.lockNode(str(obj), l=False)  # node must be unlocked to add an attribute
                    obj.addAttr("DCC_Alembic_Export_Flag", dv=True, at=bool, h=False, k=True)

            qd.info("tag successful!")
