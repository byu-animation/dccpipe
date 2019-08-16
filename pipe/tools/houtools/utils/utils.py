import hou

def houdini_main_window():
    return hou.ui.mainQtWindow()

def layout_object_level_nodes():
    node = hou.node("/obj")
    node.layoutChildren()
