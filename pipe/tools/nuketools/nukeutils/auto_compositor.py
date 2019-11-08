import os
import nuke

from pipe.am.project import Project
from pipe.am.environment import Department
from pipe.am.environment import Environment
import pipe.gui.select_from_list as sfl
import pipe.gui.quick_dialogs as qd
from pipe.tools.nuketools.nukeutils import utils


class AutoCompositor:

    def __init__(self):
        pass

    def auto_comp(self):
        nodes = nuke.allNodes()
        leafNodes = []
        mergeNodes = []

        reads = False
        for node in nodes:
            if node.Class() == 'Read':
                reads = True
                name = node.fullName()

                color_correct_node = nuke.nodes.ColorCorrect(label=name,inputs=[node])
                hue_shift_node = nuke.nodes.HueShift(label=name,inputs=[color_correct_node])
                hue_shift_node['postage_stamp'].setValue(True)
                leafNodes.append(hue_shift_node)

        if reads:
            merge = nuke.createNode("Merge")
            for i in range(len(leafNodes)):
                if i >= 2:
                    merge.setInput(i+1, leafNodes[i])
                else:
                    merge.setInput(i, leafNodes[i])

            merge['postage_stamp'].setValue(True)

            selection = os.environ.get("DCC_NUKE_ASSET_NAME")
            if not selection or selection == "":
                comp_filepath = ""
            else:
                shot = Project().get_body(selection)
                comp_element = shot.get_element(Department.COMP)
                comp_filepath = str(comp_element.get_cache_dir())
                comp_filepath = os.path.join(comp_filepath, str(selection) + ".####.jpg")

            write = nuke.createNode("Write", "file " + str(comp_filepath))
            write.setInput(0, merge)

            viewer = nuke.createNode("Viewer")
            viewer.setInput(0, merge)
