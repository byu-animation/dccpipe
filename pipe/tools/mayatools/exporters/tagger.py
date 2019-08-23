from pymel.core import *
from pipe.gui import quick_dialogs as qd
from pipe.tools.mayatools.utils.utils import *


class Tagger:
    def __init__(self):
        self.selected_string = self.get_selected_string()

    def tag(self):
        response = qd.binary_option("Add Alembic tag to:\n" + str(self.selected_string), "Yes", "No", title='Add Alembic Tag')

        if response:
            for node in self.selected:
                tag_node_with_flag(node, "DCC_Alembic_Export_Flag")

            qd.info("tag successful!")

    def untag(self):
        response = qd.binary_option("Remove Alembic tag from:\n" + str(self.selected_string), "Yes", "No", title='Remove Alembic Tag')

        if response:
            for node in self.selected:
                untag_node_with_flag(node, "DCC_Alembic_Export_Flag")

            qd.info("untag successful!")

    def displaytag(self):
        tagged_items=[]

        for node in self.all:
        #     if(node_is_tagged_with_flag(node,"DCC_Alembic_Export_Flag"))
        #     {
        #         tagged_itmes.append(node)
        #     }
        #
        #
        # print(tagged_itmes)


    def get_selected_string(self):
        self.selected = ls(sl=True, tr=True)
        self.all = ls(tr=True)
        selected_string = ""

        for node in self.selected:
            selected_string += node

        return selected_string
