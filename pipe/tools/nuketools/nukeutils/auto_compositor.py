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
        nodes = nuke.selectedNodes()
        leafNodes = []
        mergeNodes = []

        for node in nodes:
            if node.Class() == 'Read':
                channels = node.channels()
                layers = list( set([channel.split('.')[1] for channel in channels]) )
                layers.sort()

                for layer in layers:
                    # shuffle_node = nuke.nodes.Shuffle(label=layer,inputs=[node])
                    # shuffle_node['in'].setValue( layer )
                    # shuffle_node['postage_stamp'].setValue(True)
                    unpremult_node = nuke.nodes.Unpremult(label=layer,inputs=[node])
                    color_correct_node = nuke.nodes.ColorCorrect(label=layer,inputs=[unpremult_node])
                    hue_shift_node = nuke.nodes.HueShift(label=layer,inputs=[color_correct_node])
                    premult_node = nuke.nodes.Premult(label=layer,inputs=[hue_shift_node])
                    premult_node['postage_stamp'].setValue(True)
                    premult_node['alpha'].setValue(layer)

                    leafNodes.append(premult_node)
                    if layer == layers[-1]:
                        merge = nuke.nodes.Merge(operation='plus',inputs=leafNodes)
                        merge['postage_stamp'].setValue(True)
                        leafNodes = []
                        mergeNodes.append(merge)

        merge = nuke.nodes.Merge(operation='over',inputs=mergeNodes)
        merge['postage_stamp'].setValue(True)
