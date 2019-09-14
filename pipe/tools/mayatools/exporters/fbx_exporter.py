import os
import pymel.core as pm

from pipe.am.project import Project
from pipe.am.environment import Department


class FbxExporter:

    def auto_export(self, asset_name):

        project = Project()
        body = project.get_body(asset_name)

        element = body.get_element(Department.TEXTURE)
        #bodyName = element.get_parent() # do I need this?
        # body = project.get_body(bodyName)
        cache_dir = element.get_cache_dir()
        fbxFilePath = os.path.join(cache_dir, element.get_long_name() + '.fbx')

        pm.mel.FBXExport(f=fbxFilePath)
