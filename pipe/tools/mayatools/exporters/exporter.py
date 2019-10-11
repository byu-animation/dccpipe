import os
import pymel.core as pm

from pipe.am.project import Project
import pipe.gui.checkbox_options as co
import pipe.gui.quick_dialogs as qd
from pipe.tools.mayatools.utils.utils import *
from pipe.tools.mayatools.exporters.alembic_exporter import AlembicExporter
from pipe.tools.mayatools.exporters.fbx_exporter import FbxExporter
from pipe.tools.mayatools.exporters.json_exporter import JSONExporter


class Exporter:

    def __init__(self):
        self.body = None
        self.item_gui = None
        self.list = ["alembic", "fbx", "json", "usd"]

    def export_one(self, alembic=False, fbx=False, json=False, usd=False, methods=None):
        self.export(alembic=alembic, fbx=fbx, json=json, usd=usd, methods=methods)

    def export(self, alembic=True, fbx=True, json=True, usd=True, methods=None):
        if methods is None:
            methods = self.list

        asset_name = os.environ.get("DCC_ASSET_NAME")
        if not asset_name:
            qd.error("You must first create or clone an asset.")
            return

        self.body = Project().get_body(asset_name)

        if alembic:
            AlembicExporter().auto_export(asset_name)

        if self.body and self.body.is_asset():
            if json:
                if self.body.get_type() == AssetType.SET or self.body.get_type() == AssetType.SHOT:
                    json_export = JSONExporter()
                    json_export.go(self.body, self.body.get_type())
                else:
                    methods.remove("json")

            if fbx:
                if self.body.get_type() == AssetType.PROP or self.body.get_type() == AssetType.ACTOR:
                    FbxExporter().auto_export(asset_name)
                else:
                    methods.remove("fbx")

        if usd:
            print("USD isn't supported... yet :|")
            methods.remove("usd")

        if methods:
            qd.info("Successfully exported " + str(asset_name) + " as " + str(methods))
        else:
            qd.info("Nothing was exported.")

    def export_with_options(self):
        self.item_gui = co.CheckBoxOptions(parent=maya_main_window(), title="Select export methods:", options=self.list)
        self.item_gui.submitted.connect(self.export_results)

    def export_results(self, export_results):
        fbx = True
        alembic = True
        json = True
        usd = True
        methods=[]

        for item in export_results.items():
            if item[0] == "fbx":
                if item[1] is False:
                    fbx = False
                else:
                    methods.append("fbx")

            elif item[0] == "alembic":
                if item[1] is False:
                    alembic = False
                else:
                    methods.append("alembic")

            elif item[0] == "json":
                if item[1] is False:
                    json = False
                else:
                    methods.append("json")

            elif item[0] == "usd":
                if item[1] is False:
                    usd = False
                else:
                    methods.append("usd")

        self.export(alembic=alembic, fbx=fbx, json=json, usd=usd, methods=methods)
