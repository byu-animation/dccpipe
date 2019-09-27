import os
import pymel.core as pm

from pipe.am.project import Project
from pipe.am.environment import Department


class FbxExporter:

    def __init__(self):
        pm.loadPlugin('fbxmaya')

    def auto_export(self, asset_name):
        project = Project()
        body = project.get_body(asset_name)

        element = body.get_element(Department.TEXTURE)
        cache_dir = element.get_cache_dir()
        fbx_filepath = os.path.join(cache_dir, element.get_long_name() + '.fbx')

        print("Fbx filepath: ", fbx_filepath)
        pm.mel.FBXExport(f=fbx_filepath)
