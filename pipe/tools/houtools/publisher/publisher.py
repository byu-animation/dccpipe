import hou
import os
# from byugui import PublishWindow

from pipe.am.environment import Department
from pipe.am.environment import Environment
from pipe.am.body import Body
from pipe.am.project import Project
from pipe.am.element import Element
import pipe.gui.quick_dialogs as qd
import pipe.gui.select_from_list as sfl
from pipe.tools.houtools.utils.utils import *


class Publisher:

    def __init__(self):
        pass

    def publish_asset(self, node=None):
        self.departments = [Department.MODIFY, Department.MATERIAL, Department.HAIR, Department.CLOTH]
        self.publish(selectedHDA=node)

    def publish_tool(self, node=None):
        self.departments = [Department.HDA]
        self.publish(selectedHDA=node)

    def publish_shot(self):
        scene = hou.hipFile.name()
        self.departments = [Department.HDA, Department.LIGHTING, Department.FX]

        project = Project()
        asset_list = project.list_assets()
        self.item_gui = sfl.SelectFromList(l=asset_list, parent=houdini_main_window(), title="Select a shot to publish to")
        self.item_gui.submitted.connect(self.shot_results)

    def shot_results(self, value):
        chosen_asset = value[0]

        project = Project()
        self.body = project.get_body(chosen_asset)

        department_list = self.departments

        self.item_gui = sfl.SelectFromList(l=department_list, parent=houdini_main_window(), title="Select department for this publish")
        self.item_gui.submitted.connect(self.shot_department_results)

    def shot_department_results(self, value):
        chosen_department = value[0]

        element = self.body.get_element(chosen_department)  #, Element.DEFAULT_NAME)

        hou.hipFile.save()

        #Publish
        user = environment.get_user()
        src = "something"  # TODO!!!!!!!!!!!!!!!
        comment = "publish by " + str(user.get_username()) + " in department " + str(chosen_department)
        dst = publish_element(element, user, src, comment)


    def publish(self, selectedHDA=None):  #, departments=[Department.HDA, Department.ASSEMBLY, Department.MODIFY, Department.MATERIAL, Department.HAIR, Department.CLOTH]):
        project = Project()
        self.selectedHDA = selectedHDA

        if selectedHDA is None:
            nodes = hou.selectedNodes()

            if len(nodes) == 1:
                selectedHDA = nodes[0]
                self.selectedHDA = selectedHDA
            elif len(nodes) > 1:
                qd.error('Too many nodes selected. Please select only one node.')
                return
            else:
                qd.error('No nodes selected. Please select a node.')
                return

        if selectedHDA.type().definition() is not None:
            self.src = selectedHDA.type().definition().libraryFilePath()
            asset_list = project.list_assets()
            self.item_gui = sfl.SelectFromList(l=asset_list, parent=houdini_main_window(), title="Select an asset to publish to")
            self.item_gui.submitted.connect(self.asset_results)

        else:
            qd.error('The selected node is not a digital asset')
            return

    def asset_results(self, value):
        chosen_asset = value[0]

        project = Project()
        self.body = project.get_body(chosen_asset)

        department_list = self.departments

        self.item_gui = sfl.SelectFromList(l=department_list, parent=houdini_main_window(), title="Select department for this publish")
        self.item_gui.submitted.connect(self.department_results)

    def department_results(self, value):
        chosen_department = value[0]

        self.publish_hda(chosen_department)

    def publish_hda(self, department):
        project = Project()
        environment = Environment()
        user = environment.get_user()
        selectedHDA = self.selectedHDA
        src = self.src
        body = self.body

        comment = "publish by " + str(user.get_username()) + " in department " + str(department)
        hdaName = selectedHDA.type().name()

        # TODO: UGLY HOTFIX FOR OLD ASSEMBLY & TOOL ASSETS
        # asset_name = hdaName.replace("_" + department, "") if department not in [Department.ASSEMBLY, Department.HDA] else hdaName.replace("_main", "")
        # body = project.get_body(asset_name)

        if body is None:
            qd.error("Asset not found in pipe.")
            return

        if os.path.exists(src):
            try:
                #save node definition--this is the same as the Save Node Type menu option. Just to make sure I remember how this works - We are getting the definition of the selected hda and calling the function on it passing in the selected hda. We are not calling the funciton on the selected hda.
                selectedHDA.type().definition().updateFromNode(selectedHDA)
            except hou.OperationFailed, e:
                qd.error('There was a problem publishing the HDA to the pipeline.\n')
                print(str(e))
                return

            try:
                selectedHDA.matchCurrentDefinition()
            except hou.OperationFailed, e:
                qd.warning('There was a problem while trying to match the current definition. It\'s not a critical problem. Look at it and see if you can resolve the problem. Publish was successful.')
                print(str(e))

            element = body.get_element(department, Element.DEFAULT_NAME)
            dst = self.publish_element(element, user, src, comment)

            # # TODO: UGLY HOTFIX FOR OLD ASSEMBLY ASSETS
            # saveFile = hdaName + "_" + Element.DEFAULT_NAME + ".hdanc" if department not in [Department.ASSEMBLY, Department.HDA] else asset_name + "_" + department + "_" + Element.DEFAULT_NAME + ".hdanc"
            # dst = os.path.join(environment.get_hda_dir(), saveFile)
            print("dst ", dst)

            hou.hda.installFile(dst)
            definition = hou.hdaDefinition(selectedHDA.type().category(), selectedHDA.type().name(), dst)
            definition.setPreferred(True)
            #hou.hda.uninstallFile(src, change_oplibraries_file=False)

        else:
            qd.error('File does not exist', details=src)

    def publish_element(self, element, user, src, comment="None"):
        dst = element.publish(user.get_username(), src, comment)

        #Ensure file has correct permissions
        try:
            os.chmod(dst, 0660)
        except:
            qd.error("Error setting file permissions.")

        return dst





#publish v2 hda, abtracted so that multiple functions can call

def non_gui_publish_hda(hda=None,comment='N/A'):
	if hda is None:
		print ('Error with asset')

	project = Project()
	environment = Environment()
	user = environment.get_current_username()
	hdaName = hda.type().name()


	department=None

	if str(hda) not in Department.ALL:
		print 'v1 asset'
		department=Department.ASSEMBLY
	else:
		department=str(hda)


	asset_name = hdaName.replace("_" + department, "") if department not in [Department.ASSEMBLY, Department.HDA] else hdaName.replace("_main", "")
	body = project.get_body(asset_name)


	if body is None:
		qd.error('No asset in pipe')
		return

	#TODO: publish tools
	if body.is_tool():
		print (asset_name+' is tool')
		return
		department=Department.HDA



	hda_src = hda.type().definition().libraryFilePath()
	print hda_src
	element = body.get_element(department, Element.DEFAULT_NAME,force_create=True)

	try:
		hda.type().definition().updateFromNode(hda)
	except hou.OperationFailed, e:
		qd.error('There was a problem publishing the HDA to the pipeline.\n', details=str(e))
		return

	try:
		hda.matchCurrentDefinition()
	except hou.OperationFailed, e:
		qd.warning('There was a problem while trying to match the current definition.', details=str(e))

	dst = element.publish(user, hda_src, comment)
	#Ensure file has correct permissions
	try:
		os.chmod(dst, 0660)
	except:
		pass

	# TODO: UGLY HOTFIX FOR OLD ASSEMBLY ASSETS for v1 backwards compatability
	saveFile = hdaName + "_" + Element.DEFAULT_NAME + ".hdanc" if department not in [Department.ASSEMBLY, Department.HDA] else asset_name + "_" + department + "_" + Element.DEFAULT_NAME + ".hdanc"

	dst = os.path.join(environment.get_hda_dir(), saveFile)
	print("dst ", dst)
	hou.hda.installFile(dst)
	definition = hou.hdaDefinition(hda.type().category(), hda.type().name(), dst)
	definition.setPreferred(True)




##quick publish for v2 assets
def non_gui_publish_go(selectedHDA=None,comment=None):

	if selectedHDA != None:
		non_gui_publish_hda(selectedHDA,comment)
	else:
		qd.error('Please select a single node')
		return
