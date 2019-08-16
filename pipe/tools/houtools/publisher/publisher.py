import hou
import os
import json

from pipe.am.environment import Department
from pipe.am.environment import Environment
from pipe.am.body import Body, AssetType
from pipe.am.project import Project
from pipe.am.element import Element
import pipe.gui.quick_dialogs as qd
import pipe.gui.select_from_list as sfl
from pipe.tools.houtools.utils.utils import *


class Publisher:

    def __init__(self):
        self.dcc_geo_departments = [Department.MODIFY, Department.MATERIAL]
        self.item_gui = None

    def publish_content_hda(self, node):
        node_name = node.type().name()
        index = node_name.rfind('_')
        asset_name = node_name[:index]
        department = node_name[index+1:]

        self.body = Project().get_body(asset_name)
        src = node.type().definition().libraryFilePath()
        user = Environment().get_user()

        comment = "publish by " + str(user.get_username()) + " in department " + str(department)

        self.publish_src_node_to_department(src, node, department, user, comment)

        success_message = "Success! Published " + asset_name + " to " + str(department)
        self.print_success_message(success_message)

    def publish_asset(self, node=None):
        self.departments = [Department.MODIFY, Department.MATERIAL, Department.HAIR, Department.CLOTH]
        self.publish(selectedHDA=node)

    def publish_tool(self, node=None):
        self.departments = [Department.HDA]
        self.publish(selectedHDA=node)

    def publish_set(self, node=None):
        self.departments = [Department.ASSEMBLY]

        # TODO: GOING TO HAVE TO GO INTO EACH PROP WITHIN THE SET > INSIDE AND GET THE SHOT_MODELING Node
        # TODO: THEN, TAKE THE TRANSFORM DATA THERE AND SOMEHOW SAVE IT TO THE JSON SET FILE THAT STORES THE LOCATIONS
        project = Project()
        set_list = project.list_sets()
        self.item_gui = sfl.SelectFromList(l=set_list, parent=houdini_main_window(), title="Select a set to publish to")
        self.item_gui.submitted.connect(self.set_results)

    def set_results(self, value):
        set_name = value[0]

        project = Project()
        self.body = project.get_body(set_name)

        obj = hou.node("/obj")
        set = obj.node(set_name)

        if set is None:
            qd.error("No set found with that name. Please check naming and try again.")
            return

        set_file = os.path.join(Project().get_assets_dir(), set_name, "model", "main", "cache", "whole_set.json")
        print("set file: ", set_file)

        try:
            with open(set_file) as f:
                set_data = json.load(f)
        except Exception as error:
            qd.error("No valid JSON file for " + str(set_name))
            return

        print("set data: ", set_data)

        # TODO: for each child, make sure that it exists in whole_set.json

        print("set: ", set)
        inside = set.node("inside")

        children = inside.children()

        for child in children:
            print("child: ", child)

            # get transform parms: t is translate, r rotate and s scale (with associated x,y,z vals)
            tx = child.parm("tx")
            ty = child.parm("ty")
            tz = child.parm("tz")
            rx = child.parm("rx")
            ry = child.parm("ry")
            rz = child.parm("rz")
            sx = child.parm("sx")
            sy = child.parm("sy")
            sz = child.parm("sz")

            child_path = child.path()
            name = child_path.split('/')[-1]
            print("name: ", name)
            name = name.lower()


            # TODO: for each child, update their json file with transform info
            prop_file = os.path.join(Project().get_assets_dir(), set_name, "model", "main", "cache", str(name) + "_0.json")
            print("file: ", prop_file)

            prop_data = None

            try:
                with open(prop_file) as f:
                    prop_data = json.load(f)
            except Exception as error:
                qd.warning("No valid JSON file for " + str(name) + ". Skipping changes made to this asset.")
                continue

            print("prop data: ", prop_data)
            a = prop_data['a']
            b = prop_data['b']
            c = prop_data['c']

            # TODO: UPDATE THE PROP DATA FILES





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
        src = "something"  # TODO!!!!!!!!!!!!!!! TODO!!!!!!!!!!!!!!! TODO!!!!!!!!!!!!!!! TODO!!!!!!!!!!!!!!!TODO!!!!!!!!!!!!!!! TODO!!!!!!!!!!!!!!!
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
            asset_list = project.list_props_and_characters()
            self.item_gui = sfl.SelectFromList(l=asset_list, parent=houdini_main_window(), title="Select an asset to publish to")
            self.item_gui.submitted.connect(self.asset_results)

        else:
            qd.error('The selected node is not a digital asset')
            return

    def asset_results(self, value):
        chosen_asset = value[0]

        project = Project()
        self.body = project.get_body(chosen_asset)
        self.publish_hda()

    def publish_hda(self):
        project = Project()
        environment = Environment()
        user = environment.get_user()
        selectedHDA = self.selectedHDA
        src = self.src
        body = self.body
        asset_type = body.get_type()

        inside = selectedHDA.node("inside")
        modify = inside.node("modify")
        material = inside.node("material")
        hair = inside.node("hair")
        cloth = inside.node("cloth")

        if asset_type == AssetType.CHARACTER:
            geo = inside.node("geo")
            geo_inside = geo.node("inside")
            modify = geo_inside.node("modify")
            material = geo_inside.node("material")

        departments_to_publish = []

        if not modify is None:
            departments_to_publish.append("modify")
        if not material is None:
            departments_to_publish.append("material")
        if not hair is None:
            departments_to_publish.append("hair")
        if not cloth is None:
            departments_to_publish.append("cloth")

        if body is None:
            qd.error("Asset not found in pipe.")
            return

        comment = "publish by " + str(user.get_username()) + " in departments " + str(departments_to_publish)

        for department in departments_to_publish:
            inside = self.get_inside_node(asset_type, department, selectedHDA)
            node = inside.node(department)
            src = node.type().definition().libraryFilePath()

            self.publish_src_node_to_department(src, node, department, user, comment)

        success_message = "Success! Published to " + str(departments_to_publish)
        self.print_success_message(success_message)

        return "published to " + str(departments_to_publish)

    def get_inside_node(self, type, department, node):
        # If it's a character and it's not a hair or cloth asset, we need to reach one level deeper.
        if type == AssetType.CHARACTER and department in self.dcc_geo_departments:
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

            try:
                node.matchCurrentDefinition()  # this function locks the node for editing.
            except hou.OperationFailed, e:
                qd.warning('There was a problem while trying to match the current definition. It\'s not a critical problem. Look at it and see if you can resolve the problem. Publish was successful.')
                print(str(e))

            element = self.body.get_element(department, Element.DEFAULT_NAME)
            dst = self.publish_element(element, user, src, comment)

            print("dst: ", dst)

            hou.hda.installFile(dst)
            definition = hou.hdaDefinition(node.type().category(), node.type().name(), dst)
            definition.setPreferred(True)

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
