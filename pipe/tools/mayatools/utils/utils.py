# Interfacing with maya through pymel commands
import pymel.core as pm
import os
import glob
import re
from PySide2 import QtWidgets

from pipe.am import *
from pipe.am.environment import Environment
from pipe.am.environment import Department
from pipe.am.project import Project
from pipe.am.element import Element
from pipe.am.body import Body, AssetType
import pipe.gui.quick_dialogs as qd
from pipe.tools.mayatools.exporters.alembic_exporter import AlembicExporter
from pipe.tools.mayatools.exporters.json_exporter import JSONExporter

import maya.cmds as mc


'''
    Function used whenever a more complex gui is called within Maya
'''
def maya_main_window():
    for obj in QtWidgets.qApp.topLevelWidgets():
        if obj.objectName() == 'MayaWindow':
            return obj
    raise RuntimeError('Could not find MayaWindow instance')

'''
    Prepare the scene for a publish. Called from creator and publisher.
'''
def prepare_scene_file():
    filePath = mc.file(q=True, sceneName=True)

    if not filePath:
        filePath = Environment().get_user_workspace()
        filePath = os.path.join(filePath, 'untitled.mb')
        filePath = pipeline_io.version_file(filePath)
        mc.file(rename=filePath)
        mc.file(save=True)

'''
    Publish the asset. Called from creator and publisher.
'''
def post_publish(element, user, published=True, comment="No comment."):
    scene_file, created_new_file = get_scene_file()

    if published:
        if not mc.file(q=True, sceneName=True) == '':
            mc.file(save=True, force=True) #save file

        scene_prep()

        username = user.get_username()
        dst = element.publish(username, scene_file, comment)

        #Ensure file has correct permissions
        try:
            os.chmod(dst, 0660)
        except:
            print("Setting file permissions failed badly.")

        # Export JSON
        print('Publish Complete. Begin Exporting JSON if set.')
        body = Project().get_body(element.get_parent())

        if body and body.is_asset():
            if body.get_type() == AssetType.SET or body.get_type() == AssetType.SHOT:
                json_export = JSONExporter()
                json_export.go(body, body.get_type())

        print("begin alembic export")
        alembic = AlembicExporter()
        alembic.auto_export(body.get_name())

        convert_to_education()

'''
    Helper function for post_publish()
'''
def get_scene_file():
    filename = pm.system.sceneName()
    if not filename:
        filename = os.environ['HOME']
        filename = os.path.join(filename, 'untitled.mb')
        return filename, True
    else:
        return filename, False

'''
    Helper function for post_publish()
'''
def scene_prep():
    try:
        clear_construction_history()
    except:
        qd.warning("Clear construction history failed. There may be something unusual in the history that's causing this.")

    try:
        freeze_transformations()
    except:
        qd.warning("Freeze transform failed. There may be 1+ keyframed values in object. Remove all keyframed values and expressions from object.")

    try:
        delete_image_planes()
    except:
        qd.warning("Delete image planes failed.")

    try:
        group_top_level()
    except:
        qd.warning("Group top level failed.")

'''
    Helper function for scene_prep()
'''
def clear_construction_history():
    pm.delete(constructionHistory=True, all=True)

'''
    Helper function for scene_prep()
'''
def freeze_transformations():
    failed = []
    objects = pm.ls(transforms=True)
    for scene_object in objects:
        try:
            pm.makeIdentity(scene_object, apply=True)
        except:
            failed.append(scene_object)
    return failed

'''
    Helper function for post_publish()
'''
def convert_to_education():
    pm.FileInfo()['license'] = 'education'
    fileName = pm.sceneName()
    pm.saveFile()
    # qd.info('This Maya file has been converted to an education licence')

'''
    Helper function for group_top_level()
'''
def get_top_level_nodes():
    assemblies = pm.ls(assemblies=True)
    pm.select(pm.listCameras(), replace=True)
    cameras = pm.selected()
    pm.select([])
    return [assembly for assembly in assemblies if assembly not in cameras]

'''
    Helper function for scene_prep()
'''
def group_top_level():
    top_level_nodes = get_top_level_nodes()
    print("top level nodes: ", top_level_nodes)
    # If the top level has more than one node, group it.
    # Also, if there's only one top level, and it's not a group, group it.

    if len(top_level_nodes) > 1:
        pm.group(top_level_nodes)
    elif len(top_level_nodes) == 1:
        node = top_level_nodes[0]
        shapes = node.listRelatives(shapes=True)
        if not shapes and "group" not in str(node):
            pm.group(top_level_nodes)

def get_departments_by_type(asset_type):
    department_list = []
    project = Project()

    if asset_type == AssetType.PROP:
        department_list = project.prop_export_departments()
    elif asset_type == AssetType.ACTOR:
        department_list = project.char_export_departments()
    elif asset_type == AssetType.SET:
        department_list = project.set_export_departments()
    elif asset_type == AssetType.SHOT:
        department_list = project.shot_export_departments()

    return department_list

'''
    Helper function for scene_prep()
'''
def delete_image_planes():
    objects = pm.ls()
    for scene_object in objects:
        if isinstance(scene_object, pm.nodetypes.ImagePlane):
            pm.delete(scene_object)

'''
    Helper for JSONExporter and AlembicExporter
'''
def get_loaded_references():
    references = pm.ls(references=True, transforms=True)
    loaded=[]

    for ref in references:
        print "Checking status of " + ref
        try:
            if ref.isLoaded():
                loaded.append(ref)
        except:
            print "Warning: " + ref + " was not associated with a reference file"

    print("loaded: ", loaded)
    return loaded

'''
    Helper for JSONExporter
'''
def ref_path_to_ref_name(path):
    pathItems = str(path).split("/")

    for i in range(len(pathItems)):
        if pathItems[i - 1] == "assets":
            return pathItems[i]

'''
    Helper for get_body_from_reference()
'''
def extract_reference_data(ref):
    refPath = pm.referenceQuery(unicode(ref), filename=True)
    refName = ref_path_to_ref_name(refPath)
    start = refPath.find('{')
    end = refPath.find('}')

    if start == -1 or end == -1:
        vernum = ''
    else:
        vernum = refPath[start+1:end]

    return refName, vernum

'''
    Helper for JSONExporter
'''
def strip_reference(input):
    i = input.rfind(":")

    if i == -1:
        return input

    return input[i + 1:]

'''
    Helper for JSONExporter
'''
def find_first_mesh(rootNode):
    firstMesh = None
    path = ""
    stack = []
    stack.append(rootNode)
    while len(stack) > 0 and firstMesh is None:
        curr = stack.pop()
        path = path + "/" + strip_reference(curr.name())
        for child in curr.getChildren():
            if isinstance(child, pm.nodetypes.Shape):
                firstMesh = child
                path = path + "/" + strip_reference(child.name())
                break
            elif not isinstance(child, pm.nodetypes.Transform):
                continue
            if child.getShape() is not None:
                firstMesh = child.getShape()
                path = path + "/" + strip_reference(child.name()) + "/" + strip_reference(child.getShape().name())
                break
        for child in curr.getChildren():
            stack.append(child)

    return firstMesh, path

'''
    Helper for JSONExporter
'''
def get_anchor_points(mesh):
    verts = mesh.vtx
    vertpos1 = verts[0].getPosition(space='world')
    vertpos2 = verts[1].getPosition(space='world')
    vertpos3 = verts[2].getPosition(space='world')

    return vertpos1, vertpos2, vertpos3

'''
    Helper for JSONExporter
'''
def get_body_from_reference(ref):
    try:
        body = Project().get_body(extract_reference_data(ref)[0])
        return body
    except:
        print(str(ref) + " is not a body")

    return None

'''
    Helper for JSONExporter and AlembicExporter
'''
def get_root_node_from_reference(ref):
    refPath = pm.referenceQuery(unicode(ref), filename=True)
    refNodes = pm.referenceQuery(unicode(refPath), nodes=True )
    rootNode = pm.ls(refNodes[0])[0]
    return rootNode

'''
    Helper for JSONExporter
'''
def has_parent_set(rootNode):
    project = Project()
    parent_is_set = False
    parent_node = rootNode.getParent()

    while parent_node is not None:
        print("parent node: ", parent_node)
        parent_body = get_body_from_reference(parent_node)
        print("parent body: ", parent_body)

        if parent_body is not None and parent_body.is_asset() and parent_body.get_type() == AssetType.SET:
            parent_is_set = True
            break

        try:
            parent_node = parent_node.parent_node()
        except:
            print(str(parent_node) + " is top level")
            parent_node = None

    if parent_is_set:
        return True

    return False

'''
    Helpers for Tagging nodes with flags
'''

def tag_node_with_flag(node, flag):
    if not node_is_tagged_with_flag(node, flag):
        pm.cmds.lockNode(str(node), l=False)
        node.addAttr(flag, dv=True, at=bool, h=False, k=True)

def untag_node_with_flag(node, flag):
    if node_is_tagged_with_flag(node, flag):
        node.deleteAttr(flag)

def node_is_tagged_with_flag(node, flag):
    if node.hasAttr(flag):
        return True

def children_tagged_with_flag(node, flag):
    for child in node.listRelatives(allDescendants=True):
        if node_is_tagged_with_flag(child, flag):
            return True
    return False

def get_first_child_with_flag(node, flag):
    stack = []
    stack.append(node)
    while len(stack) > 0:
        curr = stack.pop()
        for child in curr.getChildren():
            if node_is_tagged_with_flag(child, flag):
                return child
        for child in curr.getChildren():
            stack.append(child)

'''
    Save the scene file. Called from education.py shelf tool.
'''
def save_scene_file():
    filename, untitled = get_scene_file()
    if untitled:
        pm.system.renameFile(filename)
    return pm.system.saveFile()
