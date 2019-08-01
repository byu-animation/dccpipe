qdfrom am import *
from gui import quick_dialogs
import os
import shutil

import maya.cmds as mc
from pymel.core import *

import pipe.am.pipeline_io as pio
from pipe.tools.mayatools.utils.utils import *
from pipe.am.environment import Environment
from pipe.am.body import AssetType
from pipe.am.project import Project
from pipe.gui import quick_dialogs as qd


class AlembicExporter:
    def __init__(self, frame_range, gui=True, element=None, show_tagger=False):
        self.frame_range = frame_range
        pm.loadPlugin('AbcExport')

    def abcExport(self, selected, path):
    	if not os.path.exists(path):
    		os.makedirs(path)

    	abcfiles = []

    	for geo in selected:
    		chop = geo.rfind('|')
    		parent_geo = geo[:chop]
    		abcFile = geo[(chop+1):]
    		abcFile = formatFilename(abcFile) + '.abc'
    		abcFilePath = os.path.join(path, abcFile)
    		print abcFilePath
    		command = 'AbcExport -j "-frameRange 1 1 -stripNamespaces -root '+parent_geo+' -nn -uv -as -file '+abcFilePath+'";'
    		print command
    		Mel.eval(command)
    		abcfiles.append(abcFilePath)

    	return abcfiles

    def abcExportLoadedReferences(self, path):
    	if not os.path.exists(path):
    		os.makedirs(path)

    	abcfiles = []

    	loadedRefs = get_loaded_references()
    	for i, ref in enumerate(loadedRefs):
    		print ref
    		refNodes = mc.referenceQuery(unicode(ref), nodes=True)
    		rootNode = ls(refNodes[0])
    		roots_string = ''
    		#TODO check if the root has been tagged
    		# if not check to see if its children have been tagged
    		# At this point we have a node that is ready for export
    		for alem_obj in rootNode:
    			roots_string += (' -root %s'%(alem_obj))

    		print 'roots_string: ' + roots_string

    		abcFile = formatFilename(ref) + '.abc'
    		abcFilePath = os.path.join(path, abcFile)
    		print 'The file path: ' + str(abcFilePath)
    		command = 'AbcExport -j "%s -frameRange 1 1 -stripNamespaces -writeVisibility -noNormals -uvWrite -worldSpace -autoSubd -file %s"'%(roots_string, abcFilePath)
    		print 'The command: ' + command
    		Mel.eval(command)
    		print 'Export successful! ' + str(i) + ' of ' + str(len(loadedRefs))
    		abcfiles.append(abcFilePath)

    	print 'all exports complete'
    	return abcfiles

    def abcExportAll(self, name, path):
    	if not os.path.exists(path):
    		os.makedirs(path)

    	abcFile = name + '.abc'
    	abcFilePath = os.path.join(path, abcFile)

    	command = 'AbcExport -j "-frameRange 1 ' + self.frame_range + ' -stripNamespaces -writeVisibility -noNormals -uvWrite -worldSpace -autoSubd -file ' + abcFilePath + '";'
        print(command)
    	Mel.eval(command)

    	abcFiles = []

    	abcFiles.append(abcFilePath)

    	return abcFiles

    def formatFilename(self, filename):
    	filename = filename.replace('Shape', '')
    	filename = filename.replace('RN', '')
    	filename = pio.alphanumeric(filename)
    	return filename

    def checkFiles(self, files):
    	'''
    		Checks the list of output files against which files were actually created
    		@param: files - a list of strings representing full paths
    		@return: a list of paths to files that do not exist
    	'''

    	missingFiles = []

    	for filename in files:
    		print 'CHECKING********** ' + filename
    		if not os.path.exists(filename):
    			missingFiles.append(filename)

    	if not len(missingFiles) == 0:
    		errorMessage = ''
    		for f in missingFiles:
    			errorMessage += 'MISSING FILE: ' + f + '\n'
    		print(errorMessage)
    		errorMessage = str(len(missingFiles)) + ' Files Missing:\n\n' + errorMessage
    		#mc.confirmDialog(title='Error exporting files', message=errorMessage)
    		#ui.infoWindow(errorMessage, wtitle='Error exporting files', msev=messageSeverity.Error)

    	return missingFiles

    def getElementCacheDirectory(self, path, element=None):

    	if element is None:
    		proj = Project()
    		checkout = proj.get_checkout(path)
    		if checkout is None:
    			qd.error('There was a problem exporting the alembic to the correct location. Checkout the asset again and try one more time.')
    			return None
    		body = proj.get_body(checkout.get_body_name())
    		element = body.get_element(checkout.get_department_name(), checkout.get_element_name())

    	return element.get_cache_dir()

    def installGeometry(self, path='',element=None):

    	'''
    		Function to install the geometry into the PRODUCTION asset directory
    		@return: True if the files were moved successfully
    		@throws: a shutil exception if the move failed
    	'''

    	path=os.path.dirname(mc.file(q=True, sceneName=True))

    	srcABC = os.path.join(path, 'cache', 'abcFiles')
    	destABC = self.getElementCacheDirectory(path, element)
    	if destABC is None:
    		return False

    	if os.path.exists(destABC):
    		try:
    			shutil.rmtree(destABC)
    		except Exception as e:
    			print 'Couldn\'t delete old abc files:'
    			print e

    	srcABC = os.path.join(srcABC, '*');
    	if not os.path.exists(destABC):
    		os.mkdir(destABC);
    		os.system('chmod 774 -R ' + destABC)

    	print 'Copying '+srcABC+' to '+destABC
    	try:
    		os.system('chmod 774 -R '+srcABC)
    		result = os.system('mv -f '+srcABC+' '+destABC)
    		print result
    		# shutil.copytree(src=srcABC, dst=destABC)

    	except Exception as e:
    		print 'Couldn\'t copy newly generated abc files:'
    		print e

    	print 'Removing '+os.path.join(path, 'cache')
    	shutil.rmtree(os.path.join(path, 'cache'))

    	return True

    def generateGeometry(self, path='',element=None):
    	'''
    		Function for generating geometry for Maya files.
    		Creates the following output formats:
    			.obj
    		@return: True if all files were created successfully
    				False if some files were not created
    		@post: Missing filenames are printed out to both the Maya terminal as well
    				as presented in a Maya confirm dialog.
    	'''

    	path = os.path.dirname(mc.file(q=True, sceneName=True))
    	if not os.path.exists (os.path.join(path, 'cache')):
    		os.makedirs(os.path.join(path, 'cache'))

    	ABCPATH = os.path.join(path, 'cache', 'abcFiles')

    	if os.path.exists(ABCPATH):
    		shutil.rmtree(ABCPATH)

    	filePath = mc.file(q=True, sceneName=True)
    	fileDir = os.path.dirname(filePath)

    	abcFilePath = self.getElementCacheDirectory(fileDir, element)
    	if abcFilePath is None:
    		return False

    	selection = mc.ls(geometry=True, visible=True)
    	selection_long = mc.ls(geometry=True, visible=True, long=True)

    	proj = Project()
    	if element is None:
    		checkout = proj.get_checkout(path)
    		if checkout is None:
    			qd.error('There was a problem exporting the alembic to the correct location. Checkout the asset again and try one more time.')
    			return None
    		body = proj.get_body(checkout.get_body_name())
    		element = body.get_element(checkout.get_department_name(), checkout.get_element_name())
    	else:
    		body = proj.get_body(element.get_parent())

    	# We decided to try exporting all the geo into one alembic file instead of many. This is the line that does many
    	# abcs = abcExport(selection_long, ABCPATH)
    	# if body.is_asset():
    	# 	if body.get_type() == AssetType.SET:
    	# 		abcs = self.abcExportLoadedReferences(ABCPATH)
    	# 	else:
    	# 		abcs = self.abcExportAll(element.get_long_name(), ABCPATH)
    	# else:

    	abcs = self.abcExportAll(element.get_long_name(), ABCPATH)

    	if not len(self.checkFiles(abcs)) == 0:
    		return False

    	return True

    def static_export(self, element=None):
    	if self.generateGeometry(element=element):
    		self.installGeometry(element=element)

    def go(self, element=None, dept=None, selection=None, startFrame=1, endFrame=1):
        endFrame = self.frame_range
        proj = Project()

        if not pm.sceneName() == '':
            pm.saveFile(force=True)

        if element is None:
            filePath = pm.sceneName()
            fileDir = os.path.dirname(filePath)
            checkout = proj.get_checkout(fileDir)
            if checkout is None:
                parent = QtWidgets.QApplication.activeWindow()
                element = selection_gui.getSelectedElement(parent)
                if element is None:
                    return None
            else:
                bodyName = checkout.get_body_name()
                deptName = checkout.get_department_name()
                elemName = checkout.get_element_name()
                body = proj.get_body(bodyName)
                element = body.get_element(deptName, name=elemName)

            #Get the element from the right Department
        if dept is not None and not element.get_department() == dept:
            print 'We are overwriting the', element.get_department(), 'with', dept
            body = proj.get_body(element.get_parent())
            element = body.get_element(dept)

        return self.export(element, selection=selection, startFrame=startFrame, endFrame=endFrame)

    def export(self, element, selection=None, startFrame=None, endFrame=None):
        proj = Project()
        bodyName = element.get_parent()
        body = proj.get_body(bodyName)
        abcFilePath = element.get_cache_dir()
        #TODO we don't want to put them into the element cache right away. We want to put them in a seperate place and then copy them over later.

        if startFrame is None:
            startFrame = pm.playbackOptions(q=True, animationStartTime=True)
        if endFrame is None:
            endFrame = pm.playbackOptions(q=True, animationEndTime=True)

        if body.is_shot():
            startFrame -= 5
            endFrame = int(endFrame)
            endFrame += 5
            endFrame = str(endFrame)
            files = self.exportReferences(abcFilePath, tag='DCC_Alembic_Export_Flag', selectionMode=True, startFrame=startFrame, endFrame=endFrame)
            result = qd.yes_or_no('Are there any crowds that need to be exported?')
            if result:
                self.exportCrowd(abcFilePath, 'DCC_Crowd_Agent_Flag', tag='DCC_Alembic_Export_Flag', startFrame=startFrame, endFrame=endFrame)
        elif body.is_asset():
            if body.get_type() == AssetType.SET:
                files = self.exportReferences(abcFilePath)
            else:
                files = self.exportAll(abcFilePath, element=element)
        elif body.is_crowd_cycle():
            files = self.exportAll(abcFilePath, tag='DCC_Alembic_Export_Flag', startFrame=startFrame, endFrame=endFrame, element=element)

        if not files:
            #Maybe this is a bad distinction but None is if it was canceled or something and empty is if it went but there weren't any alembics
            if files is None:
                return
            qd.error('No alembics were exported')
            return

        for abcFile in files:
            os.system('chmod 774 ' + abcFile)

        #TODO install the geometry
        print 'These are the files that we are returning', files
        return files


    def exportSelected(self, selection, destination, tag=None, startFrame=1, endFrame=1, disregardNoTags=False):
        abcFiles = []
        for node in selection:
            abcFilePath = os.path.join(destination, str(node) + '.abc')
            try:
                command = self.buildTaggedAlembicCommand(node, abcFilePath, tag, startFrame, endFrame)
                print 'Command:', command
            except e:
                if disregardNoTags:
                    continue
                qd.error('Unable to locate Alembic Export tag for ' + str(node), title='No Alembic Tag Found')
                continue
            print 'Export Alembic command: ', command
            pm.Mel.eval(command)
            abcFiles.append(abcFilePath)
        return abcFiles

    def exportAll(self, destination, tag=None, startFrame=1, endFrame=1, element=None):
        if tag is not None:
            selection = pm.ls(assemblies=True)
            return self.exportSelected(selection, destination, tag='DCC_Alembic_Export_Flag', startFrame=startFrame, endFrame=endFrame, disregardNoTags=True)
        else:
            return self.static_export(element=element)

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

    def exportReferences(self, destination, tag=None, selectionMode=False, startFrame=1, endFrame=1):
        if selectionMode:
            selection = reference_selection.getSelectedReferences()
        else:
            selection = reference_selection.getLoadedReferences()

        if selection is None:
            return

        abcFiles = []

        for ref in selection:
            # refNodes = cmds.referenceQuery(unicode(ref), nodes=True)
            refPath = pm.referenceQuery(unicode(ref), filename=True)
            print 'the refpath', refPath
            refNodes = pm.referenceQuery(unicode(refPath), nodes=True )
            print 'the refNode', refNodes
            rootNode = pm.ls(refNodes[0])[0]
            print 'rootNode', rootNode
            refAbcFilePath = os.path.join(destination, self.getFilenameForReference(rootNode))
            print refAbcFilePath
            try:
                if tag is None:
                    command = self.buildAlembicCommand(refAbcFilePath, startFrame, endFrame, geoList=[rootNode])
                else:
                    command = self.buildTaggedAlembicCommand(rootNode, refAbcFilePath, tag, startFrame, endFrame)
                print 'Command:', command
            except e:
                qd.error('Unable to locate Alembic Export tag for ' + str(ref), title='No Alembic Tag Found')
                return
            print 'Export Alembic command: ', command
            pm.Mel.eval(command)
            abcFiles.append(refAbcFilePath)
        return abcFiles

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

    def buildTaggedAlembicCommand(self, rootNode, filepath, tag, startFrame, endFrame, step=0.25):
        # First check and see if the reference has a tagged node on it.
        taggedNodes = self.getTaggedNodes(rootNode, tag)

        if not taggedNodes:
            print("No tagged nodes")

            # Visualize References and tags
        print rootNode
        print 'Tagged:', taggedNodes

        return self.buildAlembicCommand(filepath, startFrame, endFrame, step=step, geoList=taggedNodes)

    def buildAlembicCommand(self, outFilePath, startFrame, endFrame, step=0.25, geoList=[]):
        # This determines the pieces that are going to be exported via alembic.
        roots_string = ''

        # Each of these should be in a list, so it should know how many to add the -root tag to the alembic.
        for alem_obj in geoList:
            print 'alem_obj: ' + alem_obj
            roots_string += (' -root %s'%(alem_obj))
        print 'roots_string: ' + roots_string

        # Then here is the actual Alembic Export command for Mel.
        command = 'AbcExport -j "%s -frameRange %s %s -stripNamespaces -step %s -writeVisibility -noNormals -uvWrite -worldSpace -file %s"'%(roots_string, str(startFrame), str(endFrame), str(step), outFilePath)
        print 'Command', command
        return command

    def getTaggedNodes(self, node, tag):
        # Looks for a tagged node that has the DCC Alembic Export flag on it.
        # If the parent has a tag all the children will be exported
        print 'has attr?', node, tag
        if node.hasAttr(tag):
            return [node]

        print 'children'
        #Otherwise search all the children for any nodes with the flag
        tagged_children = []
        for child in node.listRelatives(c=True):
            tagged_children.extend(getTaggedNodes(child, tag))

        return tagged_children
