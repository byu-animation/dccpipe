from am import *
from gui import quick_dialogs
import os
import shutil

import maya.cmds as mc
from pymel.core import *

import pipe.am.pipeline_io as pio
from pipe.tools.mayatools.utils.utils import *
from pipe.am.environment import Environment
from pipe.am.environment import Department
from pipe.am.body import AssetType
from pipe.am.project import Project
from pipe.gui import quick_dialogs as qd
import pipe.gui.select_from_list as sfl


class AlembicExporter:
    def __init__(self, frame_range=1, gui=True, element=None, show_tagger=False):
        self.frame_range = frame_range
        pm.loadPlugin('AbcExport')
        self.crease = False

    def auto_export(self, asset_name):
        self.get_body_and_export(asset_name, export_all=True)

    def go(self):
        project = Project()
        asset_list = project.list_assets()

        self.item_gui = sfl.SelectFromList(l=asset_list, parent=maya_main_window(), title="Select an asset to export to")
        self.item_gui.submitted.connect(self.asset_results)

    def asset_results(self, value):
        chosen_asset = value[0]
        self.get_body_and_export(chosen_asset)

    def get_body_and_export(self, chosen_asset, export_all=False):
        project = Project()
        self.body = project.get_body(chosen_asset)
        type = self.body.get_type()

        if type == AssetType.PROP or type == AssetType.ACTOR:
            creases = qd.yes_or_no("Does this asset use creases?")

            if creases:
                self.crease = True

        if type == AssetType.SHOT:
            export_all = False
            self.frame_range = qd.input("Enter frame range (as numeric input) or leave blank if none:")

            if self.frame_range is None or self.frame_range == u'':
                self.frame_range = 1

            self.frame_range = str(self.frame_range)
            if not self.frame_range.isdigit():
                qd.error("Invalid frame range input. Setting to 1.")
        else:
            self.frame_range = 1

        self.body.set_frame_range(self.frame_range)

        asset_type = self.body.get_type()
        department_list = get_departments_by_type(asset_type)

        if export_all:
            # tag top level nodes
            nodes = get_top_level_nodes()
            print("top level: ", nodes)
            for node in nodes:
                tag_node_with_flag(node, "DCC_Alembic_Export_Flag")

        self.department_results(department_list)

    def department_results(self, value):
        department_list = value

        selection = None
        startFrame = 1
        endFrame = self.frame_range

        for dept in department_list:  # export to all departments selected
            element = self.body.get_element(dept)

            if not pm.sceneName() == '':
                pm.saveFile(force=True)

            if element is None:
                filePath = pm.sceneName()
                fileDir = os.path.dirname(filePath)
                checkout = project.get_checkout(fileDir)
                if checkout is None:
                    parent = QtWidgets.QApplication.activeWindow()
                    element = selection_gui.getSelectedElement(parent)
                    if element is None:
                        return None
                else:
                    bodyName = checkout.get_body_name()
                    deptName = checkout.get_department_name()
                    elemName = checkout.get_element_name()
                    body = project.get_body(bodyName)
                    element = body.get_element(deptName, name=elemName)

                #Get the element from the right Department
            if dept is not None and not element.get_department() == dept:
                print 'We are overwriting the', element.get_department(), 'with', dept
                body = project.get_body(element.get_parent())
                element = body.get_element(dept)

            self.export(element, selection=selection, startFrame=startFrame, endFrame=endFrame)

    def export(self, element, selection=None, startFrame=None, endFrame=None):
        project = Project()
        bodyName = element.get_parent()
        body = project.get_body(bodyName)
        abcFilePath = element.get_cache_dir()

        self.element = element

        if startFrame is None:
            startFrame = pm.playbackOptions(q=True, animationStartTime=True)
        if endFrame is None:
            endFrame = pm.playbackOptions(q=True, animationEndTime=True)

        if body.is_shot():
            startFrame -= 5
            endFrame = int(endFrame)
            endFrame += 5
            endFrame = str(endFrame)
            files = self.exportReferences(abcFilePath, tag='DCC_Alembic_Export_Flag', startFrame=startFrame, endFrame=endFrame)
            files.extend(self.export_cameras(body, startFrame, endFrame))

        elif body.is_asset():
            if body.get_type() == AssetType.SET:
                files = self.exportReferences(abcFilePath)
            else:
                files = self.exportAll(abcFilePath, tag='DCC_Alembic_Export_Flag', element=element)

        elif body.is_crowd_cycle():
            files = self.exportAll(abcFilePath, tag='DCC_Alembic_Export_Flag', startFrame=startFrame, endFrame=endFrame, element=element)

        if not files:
            #Maybe this is a bad distinction but None is if it was canceled or something and empty is if it went but there weren't any alembics
            if files is None:
                return
            qd.error('No alembics were exported. Make sure the top-level group is tagged.')
            return

        for abcFile in files:
            os.system('chmod 774 ' + abcFile)

        print("Alembic file(s): ", files)
        return files

    def exportSelected(self, selection, destination, tag=None, startFrame=1, endFrame=1, disregardNoTags=False):
        endFrame = self.frame_range
        abcFiles = []

        # for node in selection:
            # abcFilePath = os.path.join(destination, str(node) + '.abc')
            # print("abc file path 1: ", abcFilePath)

        abcFilePath = os.path.join(destination, self.element.get_long_name() + '.abc')

        try:
            command = self.buildTaggedAlembicCommand(abcFilePath, tag, startFrame, endFrame)
        except:
            qd.error('Alembic export failed.')

        print('Export Alembic command: ', command)
        pm.Mel.eval(command)
        abcFiles.append(abcFilePath)

        return abcFiles

    def exportAll(self, destination, tag=None, startFrame=1, endFrame=1, element=None):
        # selection = pm.ls(assemblies=True)
        #
        # culled_selection = []
        # for item in selection:
        #     if item.find("joint") == -1:
        #         culled_selection.append(item)
        # print("culled selection: ", culled_selection)
        # list = self.get_all_tagged_nodes()
        list = []

        return self.exportSelected(list, destination, tag='DCC_Alembic_Export_Flag', startFrame=startFrame, endFrame=endFrame, disregardNoTags=True)


    def exportCrowd(self, destination, crowdTag, tag=None, startFrame=1, endFrame=1):
        #Find all of the parent nodes with the crowdTag.
        # For each element in the outliner
        selection = pm.ls(assemblies=True)
        # check if it has a crowdTag inside of it.
        agents = []
        destination = os.path.join(destination, 'crowdAlembics')
        if not os.path.exists(destination):
            print "we are making the destination dir"
            os.makedirs(destination)
        else:
            print "The director was already created"
            for node in selection:
                if self.getTaggedNodes(node, crowdTag):
                    print 'the destination is', destination
                    print 'the node is', node
                    self.exportSelected([node], destination, tag='DCC_Alembic_Export_Flag', startFrame=startFrame, endFrame=endFrame)
                else:
                    print 'We did not find a tag on', node
#For each of those parent nodes export the tagged geo within

    '''
        @destination: directory where the alembic(s) should be exported to
        @tag: unused
        @startFrame: beginning frame to export
        @endFrame: ending frame to export \

        @return: a list of exported alembic files

        Gets all loaded references, then loops through them and if it's a top level reference
        i.e. a actor, set, or animated prop, exports an alembic file to the destination specified
    '''
    def exportReferences(self, destination, tag=None, startFrame=1, endFrame=1):
        selection = get_loaded_references()

        if selection is None:
            return

        abcFiles = []
        print("destination: ", destination)

        for ref in selection:
            try:
                rootNode = get_root_node_from_reference(ref)
            except:
                qd.warning("Could not find " + str(ref) + " in scene. Skipping.")
                continue

            if tag:
                if node_is_tagged_with_flag(rootNode, tag):
                    print("node is tagged: " + str(rootNode))
                else:
                    print("ref is not tagged: " + str(ref))
                    continue

            name = str(ref.associatedNamespace(baseName=True))
            parent = ref.parentReference()
            print("ref: ", ref)

            if not parent:
                # then this is either an animated prop, a char, or a set. Export an alembic for each accordingly, with the correct file name
                refAbcFilePath = os.path.join(destination, name + ".abc")
                print("ref abc filepath: ", refAbcFilePath)

                root = self.get_parent_root_string(rootNode)
                root_strings = [root]

                # if tag:
                #     command = self.buildTaggedAlembicCommand(refAbcFilePath, tag, startFrame, endFrame)
                # else:
                command = self.buildAlembicCommand(refAbcFilePath, startFrame, endFrame, geoList=root_strings)
            else:
                continue

            print 'Export Alembic command: ', command

            try:
                pm.Mel.eval(command)
            except:
                qd.warning("No alembic exported for " + str(rootNode) + ". Make sure that there is only one top-level group in the outliner.")
                continue

            abcFiles.append(refAbcFilePath)

        return abcFiles

    def export_cameras(self, shot, startFrame, endFrame):
        cam_list = mc.listCameras(p=True)

        if u'persp' in cam_list:
            cam_list.remove(u'persp')

        print("cam list: ", cam_list)
        print("shot", str(shot))

        cam_element = shot.get_element(Department.CAMERA, force_create=True)
        cache_dir = cam_element.get_cache_dir()

        print("cache dir: ", cache_dir)

        files = []

        for cam_name in cam_list:
            cameras = pm.ls(cam_name)
            camera = cameras[0]

            root = self.get_parent_root_string(camera)
            root_strings = [root]

            destination = os.path.join(cache_dir, str(cam_name) + ".abc")

            command = self.buildAlembicCommand(destination, startFrame, endFrame, geoList=root_strings)

            print 'Export Alembic command: ', command

            try:
                pm.Mel.eval(command)
            except:
                qd.warning("No alembic exported for " + str(camera) + ". Make sure that there is only one top-level group in the outliner.")
                continue

            files.append(destination)

        return files

    def getFilenameForReference(self, ref):
        #TODO Make sure that we test for multiple files
        # When we get the file name we need to make sure that we also get the reference number. This will allow us to have multiple alembics from a duplicated reference.
        # refPath = ref.fileName(False,True,True)
        refPath = refPath = pm.referenceQuery(unicode(ref), filename=True)
        start = refPath.find('{')
        end = refPath.find('}')

        if start == -1 or end == -1:
            copyNum = ''
        else:
            copyNum = refPath[start+1:end]

        return os.path.basename(refPath).split('.')[0] + str(copyNum) + '.abc'

    def buildTaggedAlembicCommand(self, filepath, tag, startFrame, endFrame, step=0.25):
        # First check and see if the reference has a tagged node on it.
        taggedNodes = self.get_all_tagged_nodes(tag)
        root_strings = []

        if not taggedNodes:
            print("No tagged nodes")

        for node in taggedNodes:
            root = self.get_parent_root_string(node)
            root_strings.append(root)

        print("roots: ", root_strings)

        return self.buildAlembicCommand(filepath, startFrame, endFrame, step=step, geoList=root_strings)

    def buildAlembicCommand(self, outFilePath, startFrame, endFrame, step=0.25, geoList=[]):
        # This determines the pieces that are going to be exported via alembic.
        roots_string = ''

        # Each of these should be in a list, so it should know how many to add the -root tag to the alembic.
        for root_string in geoList:
            roots_string += ('-root |%s '%(root_string))

        print('roots_string: ', roots_string)

        auto_sub = ""
        if self.crease is True:
            auto_sub = "-autoSubd"

        # Then here is the actual Alembic Export command for Mel. For abcExport docs, run AbcExport -h in Maya
        command = 'AbcExport -j "-frameRange %s %s -uvWrite %s -noNormals -worldSpace -dataFormat ogawa %s -file %s"'%(str(startFrame), str(endFrame), auto_sub, roots_string, outFilePath)
        return command

    def get_all_tagged_nodes(self, tag="DCC_Alembic_Export_Flag"):
        list = []

        nodes = pm.ls(assemblies=True, ca=False)
        for node in nodes:
            list.extend(self.getTaggedNodes(node, tag))

        print("tagged list: ", list)

        return list

    def get_parent_root_string(self, node):
        parents = node.listRelatives(p=True)
        if parents:
            root = ""

            while parents:
                p = parents[0]
                print("parent: ", str(p))
                root = str(p) + "|" + root
                parents = p.listRelatives(p=True)

            root += self.strip_pipe(str(node))
        else:
            root = self.strip_pipe(str(node))

        print("root: ", root)
        return root

    def strip_pipe(self, input):
        pipe = input.find("|")
        i = None
        if pipe:
                i = pipe
        else:
            return input

        return input[i + 1:]

    def getTaggedNodes(self, node, tag):
        # Looks for a tagged node that has the DCC Alembic Export flag on it.
        # If the parent has a tag all the children will be exported
        if node.hasAttr(tag):
            return [node]

        #Otherwise search all the children for any nodes with the flag
        tagged_children = []
        for child in node.listRelatives(c=True):
            tagged_children.extend(self.getTaggedNodes(child, tag))

        return tagged_children
