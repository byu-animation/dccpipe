import hou
import os
from datetime import datetime

from PySide2 import QtGui, QtWidgets, QtCore

from pipe.am.environment import Department, Environment
from pipe.am.project import Project
from pipe.am.body import AssetType
import pipe.gui.quick_dialogs as qd
from pipe.tools.houtools.utils.utils import *

class GenerateROP:

    def __init__(self):
        pass

    def go(self, node=None):
        out = hou.node("/out")
        renderNode = out.createNode("ris", "Render_OUT")

        shop = hou.node("/shop")
        risnet = shop.createNode("risnet", "Risnet_OUT")
        vcm = risnet.createNode("pxrvcm", "PxrVCM_OUT")
        pathtracer = risnet.createNode("pxrpathtracer", "PxrPathTracer_OUT")

        renderNode.parm("shop_integratorpath").set("/shop/" + str(risnet) + "/" + str(vcm))
        renderNode.parm("camera").set("/obj/dcc_camera1/_/CameraRig_Camera/CameraRig_CameraShape")
        renderNode.parm("override_camerares").set(1)
        renderNode.parm("res_fraction").set("specific")
        renderNode.parm("res_overridex").set(1920)
        renderNode.parm("res_overridey").set(1080)
        renderNode.parm("trange").set("normal")
        renderNode.parm("ri_quickaov_z_0").set(1)
        renderNode.parm("ri_device_0").set("openexr")
        renderNode.parm("allowmotionblur").set(1)

        assetDirectory = Project().get_assets_dir()
        hipName = hou.hipFile.name()
        shot = ""
        if assetDirectory in hipName:
            shot = hipName.replace(assetDirectory,'')
        #shot = shot[1:]
        shot = shot[0:shot.find("/")]
        currentDate = datetime.now().strftime("%m_%d_%y-%Hhr_%Mmin_%Ssec")
        exrName = str(shot) + ".$F4.exr"
        path = os.path.join(assetDirectory, shot, "render", "main", "cache", currentDate, exrName)
        print(path)

        renderNode.parm("ri_display_0").set(path)
