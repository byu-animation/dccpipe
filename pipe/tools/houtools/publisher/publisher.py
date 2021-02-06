import hou
import os
import json

from pipe.am.environment import Department
from pipe.am.environment import Environment
from pipe.am import pipeline_io
from pipe.am.body import Body, AssetType
from pipe.am.project import Project
from pipe.am.element import Element
import pipe.gui.quick_dialogs as qd
import pipe.gui.select_from_list as sfl
from pipe.tools.houtools.utils.utils import *
from publish_set import *


class Publisher:

    def __init__(self):
        self.dcc_geo_departments = [Department.MODIFY, Department.MATERIAL]
        self.item_gui = None
        self.node_name = None

    def publish_content_hda(self, node):
        self.node = node
        self.comment = qd.HoudiniInput(parent=houdini_main_window(), title="Any comments?")
        self.comment.submitted.connect(self.publish_content_hda_comment)

    def publish_content_hda_comment(self, value):
        node = self.node
        comment = value
        if not comment:
            comment = "published by " + str(user.get_username()) + " in department " + str(department)
        node_name = node.type().name()
        index = node_name.rfind('_')
        asset_name = node_name[:index]
        department = node_name[index+1:]

        self.body = Project().get_body(asset_name)
        src = node.type().definition().libraryFilePath()
        user = Environment().get_user()

        self.publish_src_node_to_department(src, node, department, user, comment)

        success_message = "Success! Published " + asset_name + " to " + str(department)
        self.print_success_message(success_message)

    def publish_asset(self, node=None, name=None, inner=False):
        self.departments = [Department.MODIFY, Department.MATERIAL, Department.HAIR, Department.CLOTH]

        if node:
            if inner:  # TODO: clean this up
                if node.type().name() == 'byu_inside' or node.type().name() == 'byu_objectinside':
                    node = node.parent()
                if node.parent().parent().type().name() == 'dcc_character':
                    node = node.parent().parent()

            self.node_name = node.parm("asset_name").eval()
            print("node: ", node)
            print("name: ", self.node_name)

        self.publish(selectedHDA=node)

    def publish_tool(self, node=None):
        if node is None:
            node = get_selected_node()
            if node is None:
                return

        node_path = node.path()
        name = node_path.split('/')[-1]
        tool_name = name

        tools = Project().list_hdas()
        if tool_name not in tools:
            qd.error("Tool not found in project. Try creating HDA instead.")

        try:
            node.type().definition().updateFromNode(node)
        except hou.OperationFailed, e:
            qd.error('There was a problem publishing the HDA to the pipeline.\n', details=str(e))
            return

        try:
            node.matchCurrentDefinition()
        except hou.OperationFailed, e:
            qd.warning("Problem matching description.")

        destination = os.path.join(Environment().get_hda_dir(), tool_name + ".hda")
        hou.hda.installFile(destination)
        definition = hou.hdaDefinition(node.type().category(), node.type().name(), destination)
        definition.setPreferred(True)

    def publish_set(self, node=None, name=None):
        self.departments = [Department.ASSEMBLY]
        if name:
            self.set_results([name])
            return

        project = Project()
        set_list = project.list_sets()
        self.item_gui = sfl.SelectFromList(l=set_list, parent=houdini_main_window(), title="Select a set to publish")
        self.item_gui.submitted.connect(self.set_results)

    def set_results(self, value):
        temp_publish_set = publish_set()
        temp_publish_set.set_results(value)

    def publish_shot(self):
        scene = hou.hipFile.name()
        self.departments = [Department.HDA, Department.LIGHTING, Department.FX]

        project = Project()
        asset_list = project.list_shots()
        self.item_gui = sfl.SelectFromList(l=asset_list, parent=houdini_main_window(), title="Select a shot to publish to")
        self.item_gui.submitted.connect(self.shot_results)

    def shot_results(self, value):
        self.chosen_asset = value[0]

        self.comment = qd.HoudiniInput(parent=houdini_main_window(), title="Any comments?")
        self.comment.submitted.connect(self.shot_comment)

    def shot_comment(self, value):
        comment = value
        if comment is None:
            comment = "publish by " + str(user.get_username()) + " in department " + str(department)

        chosen_asset = self.chosen_asset

        project = Project()
        self.body = project.get_body(chosen_asset)

        department = Department.LIGHTING
        element = self.body.get_element(department)  #, Element.DEFAULT_NAME)

        hou.hipFile.save()
        src = hou.hipFile.name()

        #Publish
        user = Environment().get_user()
        pipeline_io.set_permissions(src)
        dst = self.publish_element(element, user, src, comment)
        pipeline_io.set_permissions(dst)

        message = "Successfully published " + str(self.body.get_name()) + "!"
        self.print_success_message(message)

    def publish(self, selectedHDA=None):  #, departments=[Department.HDA, Department.ASSEMBLY, Department.MODIFY, Department.MATERIAL, Department.HAIR, Department.CLOTH]):
        project = Project()
        self.selectedHDA = selectedHDA

        if self.selectedHDA is None:
            self.selectedHDA = get_selected_node()
            if self.selectedHDA is None:
                return

        if self.selectedHDA.type().definition() is not None:
            self.src = self.selectedHDA.type().definition().libraryFilePath()

            if self.node_name:
                self.asset_results([self.node_name])
                return

            asset_list = project.list_props_and_actors()
            self.item_gui = sfl.SelectFromList(l=asset_list, parent=houdini_main_window(), title="Select an asset to publish to")
            self.item_gui.submitted.connect(self.asset_results)

        else:
            qd.error('The selected node is not a digital asset')

        return

    def asset_results(self, value):
        chosen_asset = value[0]

        project = Project()
        self.body = project.get_body(chosen_asset)
        self.comment = qd.HoudiniInput(parent=houdini_main_window(), title="Any comments?")
        self.comment.submitted.connect(self.publish_hda)

    def publish_hda(self, value):
        comment = value
        if not comment:
            comment = "publish by " + str(user.get_username()) + " in department " + str(department)

        project = Project()
        environment = Environment()
        user = environment.get_user()
        selectedHDA = self.selectedHDA
        if selectedHDA is None:
            print("No HDA selected!")
        src = self.src
        body = self.body
        asset_type = body.get_type()

        inside = selectedHDA.node("inside")
        if inside is None:
            print("No inside node found!")
        modify = inside.node("modify")
        material = inside.node("material")
        hair = inside.node("hair")
        cloth = inside.node("cloth")

        if asset_type == AssetType.ACTOR:
            geo = inside.node("geo")
            geo_inside = geo.node("inside")
            modify = geo_inside.node("modify")
            material = geo_inside.node("material")

        departments_to_publish = []

        if modify is not None:
            print("Found modify")
            departments_to_publish.append("modify")
        if material is not None:
            print("Found material")
            departments_to_publish.append("material")
        if hair is not None:
            departments_to_publish.append("hair")
        if cloth is not None:
            departments_to_publish.append("cloth")

        if body is None:
            qd.error("Asset not found in pipe.")
            return

        for department in departments_to_publish:
            inside = self.get_inside_node(asset_type, department, self.selectedHDA)
            node = inside.node(department)
            src = node.type().definition().libraryFilePath()

            try:
                self.publish_src_node_to_department(src, node, department, user, comment)
            except Exception as e:
                print(str(e))
                qd.warning("Something went wrong, but it's probably okay.")

        success_message = "Success! Published to " + str(departments_to_publish)
        self.print_success_message(success_message)

        return "published to " + str(departments_to_publish)

    def get_inside_node(self, type, department, node):
        # If it's a actor and it's not a hair or cloth asset, we need to reach one level deeper.
        if type == AssetType.ACTOR and department in self.dcc_geo_departments:
            inside = node.node("inside/geo/inside")
        else:
            inside = node.node("inside")

        return inside

    def publish_src_node_to_department(self, src, node, department, user, comment):
        if os.path.exists(src):
            try:
                #save node definition--this is the same as the Save Node Type menu option. Just to make sure I remember how this works - We are getting the definition of the selected hda and calling the function on it passing in the selected hda. We are not calling the function on the selected hda.
                node.type().definition().updateFromNode(node)
            except hou.OperationFailed, e:
                qd.error('There was a problem publishing the HDA to the pipeline.\n')
                print(str(e))
                return

            element = self.body.get_element(department, Element.DEFAULT_NAME)
            dst = self.publish_element(element, user, src, comment)

            print("dst: ", dst)

            try:
                hou.hda.installFile(dst)
                definition = hou.hdaDefinition(node.type().category(), node.type().name(), dst)
                definition.setPreferred(True)
                node.allowEditingOfContents()
            except Exception as e:
                qd.error("Publish failed for " + str(department), details=str(e))

        else:
            qd.error('File does not exist', details=src)

    def publish_element(self, element, user, src, comment="None"):
        dst = element.publish(user.get_username(), src, comment)

        #Ensure file has correct permissions
        try:
            os.chmod(dst, 0660)
        except Exception as e:
            print("Error setting file permissions: " + str(e))

        return dst

    def print_success_message(self, message):
        qd.info(message)

    def non_gui_publish_hda(self, hda, src, body, department):
        self.selectedHDA = hda
        self.src = src
        self.body = body

        return self.publish_hda()



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
