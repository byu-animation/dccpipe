import pipe.gui.quick_dialogs as qd
import pipe.gui.select_from_list as sfl
from pipe.am.project import Project
from pipe.am.environment import Environment
from pipe.am.body import Body
from pipe.am.body import AssetType
from pipe.tools.houtools.utils.utils import *
from pipe.am import pipeline_io
from pipe.tools.houtools.assembler.assembler import Assembler
import re
from PySide2 import QtWidgets


class Creator:

    def __init__(self):
        self.name = None
        self.type = None

    def run(self, type=None):
        self.type = type
        self.create_body()

    '''
    This will bring up the create new body UI
    '''
    def create_body(self):
        self.input = qd.HoudiniInput(parent=houdini_main_window(), title="What is the name of this asset?")
        self.input.submitted.connect(self.name_results)

    def name_results(self, value):
        self.name = str(value)

        name = str(self.name)
        if not pipeline_io.checkFileName(name):
            self.create_body()
            return

        if self.name is None or self.name == "":
            return

        asset_type_list = AssetType().list_asset_types()

        if self.type:
            self.results([self.type])
            return

        self.item_gui = sfl.SelectFromList(l=asset_type_list, parent=houdini_main_window(), title="What are you creating?", width=250, height=160)
        self.item_gui.submitted.connect(self.results)

    def results(self, value):
        type = value[0]
        name = self.name

        # determine if asset was created or not.
        created = True

        if name is None or type is None:
            created = False

        if created:
            project = Project()
            body = project.create_asset(name, asset_type=type)
            if body == None:
                # print a message about failure/duplicate
                qd.error("Asset with name " + name + " already exists in pipeline.")
            elif self.type == AssetType.SHOT:
                qd.info("Asset created successfully.", "Success")
            else:
                assembler = Assembler()
                assembler.create_hda(name, body=body)

                qd.info("Asset created successfully.", "Success")

        else:
            qd.error("Asset creation failed.")
