import os
from pymel.core import *

from pipe.am.project import Project
from pipe.am.environment import Environment


class FbxExporter:

    def auto_export():

        project = Project()
        body = project.get_body(chosen_asset)

        element = body.get_element(Environment.TEXTURE)
        #bodyName = element.get_parent() # do I need this?
        # body = project.get_body(bodyName)
        cache_dir = element.get_cache_dir()
        fbxFilePath = os.path.join(cache_dir, element.get_long_name() + '.fbx')

        pm.mel.FBXExport(s=True, f=fbxFilePath)
