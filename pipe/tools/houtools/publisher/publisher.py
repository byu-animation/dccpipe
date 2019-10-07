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
            self.node_name = name
            print("node: ", node)
            print("name: ", name)
        if inner:
            #node = 
            #name = 
            #self.node_name = name
            

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
        set_name = value[0]
        project = Project()
        self.body = project.get_body(set_name)

        obj = hou.node("/obj")
        set = obj.node(set_name)

        if set is None:
            qd.error("No set found with that name. Please check naming and try again.")
            return

        print("set: ", set)
        inside = set.node("inside")
        children = inside.children()
        set_file = os.path.join(Project().get_assets_dir(), set_name, "model", "main", "cache", "whole_set.json")

        set_data = []
        try:
            with open(set_file) as f:
                set_data = json.load(f)
        except Exception as error:
            qd.error("No valid JSON file for " + str(set_name))
            return

        items_in_set = []
        for item in set_data:
            item_name = item['asset_name']
            item_version = item['version_number']
            items_in_set.append(item_name)

        child_names = []
        for child in children:
            child_path = child.path()
            first_char_to_lower = lambda s: s[:1].lower() + s[1:] if s else ''
            name = child_path.split('/')[-1]
            name = first_char_to_lower(name)
            child_names.append(name)
        print("child names; ", child_names)

        for item in set_data:
            if str(item['asset_name']) not in child_names:
                set_data.remove(item)

        # TODO: To allow adding multiple copies of the same prop to a set in houdini, we'll want to add as many copies to the whole_set.json file
        # for child_name in child_names:
        #     child = inside.node(child_name)  # get the child node
        #     inside = child.node("inside")
        #     modify = inside.node("modify")
        #     modify_name = modify.type().name()
        #     name = modify_name.split("_")[0].lower()
        #
        #     if name not in items_in_set:
        #         set_data.append

        for child in children:
            print("child: ", child)
            inside = child.node("inside")
            out = inside.node("OUT")
            modify = inside.node("modify")
            set_transform = inside.node("set_dressing_transform")
            current_version = child.parm("version_number").evalAsInt()

            modify_name = modify.type().name()
            name = modify_name.split("_")[0]

            child_body = project.get_body(name)
            if child_body is None:
                qd.warning(str(name) + " not found in pipe. Please check that node is named correctly.")
                continue

            # get transform parms: t is translate, r rotate and s scale (with associated x,y,z vals)
            tx, ty, tz = self.get_transform(set_transform, "tx", "ty", "tz")
            rx, ry, rz = self.get_transform(set_transform, "rx", "ry", "rz")
            sx, sy, sz = self.get_transform(set_transform, "sx", "sy", "sz")

            cache_dir = os.path.join(Project().get_assets_dir(), set_name, "model", "main", "cache")
            print("filepath: ", cache_dir)
            latest_version, version_string = self.body.version_prop_json(name, cache_dir)
            print('latest version: ', latest_version)
            new_version = latest_version
            latest_version -= 1

            prop_file = os.path.join(cache_dir, str(name) + "_" + str(current_version) + ".json")
            print("prop file: ", prop_file)

            if name in items_in_set:
                print("set contains asset: " + str(name))
                try:
                    with open(prop_file) as f:
                        prop_data = json.load(f)
                except Exception as error:
                    qd.warning("No valid JSON file for " + str(name) + ". Skipping changes made to this asset.")
                    continue

                for set_item in set_data:
                    if str(set_item['asset_name']) == str(name):
                        if set_item['version_number'] == current_version:
                            print("updating ", set_item, " with version ", new_version)
                            set_item['version_number'] = new_version
                            break

            else:
                print(str(name) + " not found in set file.")
                path = self.get_prim_path(out)
                prop_data = {"asset_name": name, "version_number": 0, "path" : str(path), "a" : [0, 0, 0], "b" : [0, 0, 0], "c" : [0, 0, 0] }
                set_data.append({"asset_name": str(name), "version_number": 0})
                new_version = 0
                items_in_set.append(name)

            new_prop_file = os.path.join(Project().get_assets_dir(), set_name, "model", "main", "cache", str(name) + "_" + str(new_version) + ".json")

            # get a b and c from prop_data file. Each is an array of size 3, representing x,y,z coords
            a = prop_data['a']
            b = prop_data['b']
            c = prop_data['c']

            self.update_points_by_geo(out, a, b, c)

            # put the updated coords back into prop_data
            prop_data['a'] = a
            prop_data['b'] = b
            prop_data['c'] = c
            prop_data['version_number'] = new_version

            # TODO: add a commit and a publish for this set

            print("prop data (updated): ", prop_data)

            updated_prop_data = json.dumps(prop_data)
            outfile = open(new_prop_file, "w")
            outfile.write(updated_prop_data)
            outfile.close()

            print("prop file updated for " + str(name))

            self.clear_transform(set_transform)
            self.set_space(child, set_name, name, new_version)
            import_node = child.node("import")
            read_from_json = import_node.node("read_from_json")
            read_from_json.parm("reload").pressButton()

            outfile = open(set_file, "w")
            print("set data: ", set_data)
            updated_set_data = json.dumps(set_data)
            outfile.write(updated_set_data)
            outfile.close()

        qd.info("Set " + str(set_name) + " published successfully!")

    def get_prim_path(self, out):
        geo = out.geometry()
        return geo.findPrimAttrib("path").strings()[0]

    def update_points_by_geo(self, out, a, b, c):
        geo = out.geometry()
        point_a = geo.iterPoints()[0]
        point_b = geo.iterPoints()[1]
        point_c = geo.iterPoints()[2]

        a_x = point_a.position()[0]
        a_y = point_a.position()[1]
        a_z = point_a.position()[2]
        b_x = point_b.position()[0]
        b_y = point_b.position()[1]
        b_z = point_b.position()[2]
        c_x = point_c.position()[0]
        c_y = point_c.position()[1]
        c_z = point_c.position()[2]

        # a is the first point of this object in geo spreadsheet, b is second, c third.
        a[0] = a_x
        a[1] = a_y
        a[2] = a_z
        b[0] = b_x
        b[1] = b_y
        b[2] = b_z
        c[0] = c_x
        c[1] = c_y
        c[2] = c_z

    def get_transform(self, child, parm1, parm2, parm3):
        x = child.parm(parm1).evalAsFloat()
        y = child.parm(parm2).evalAsFloat()
        z = child.parm(parm3).evalAsFloat()

        return x, y, z

    def set_space(self, child, set_name, child_name, version_number):
        child.parm("space").set("set")
        child.parm("space").eval()
        child.parm("set").set(set_name)
        child.parm("set").eval()
        child.parm("asset_name").set(child_name)
        child.parm("asset_name").eval()
        child.parm("version_number").set(version_number)
        child.parm("version_number").eval()

    def clear_transform(self, child):
        parm_scale_list = ["sx", "sy", "sz"]
        parm_list = ["tx", "ty", "tz", "rx", "ry", "rz", "sx", "sy", "sz"]

        for parm in parm_list:
            if parm not in parm_scale_list:
                child.parm(parm).set(0.0)
            else:
                child.parm(parm).set(1.0)
            child.parm(parm).eval()

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

        if body is not None:
            qd.error("Asset not found in pipe.")
            return

        for department in departments_to_publish:
            inside = self.get_inside_node(asset_type, department, self.selectedHDA)
            node = inside.node(department)
            src = node.type().definition().libraryFilePath()

            self.publish_src_node_to_department(src, node, department, user, comment)

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
            node.allowEditingOfContents()

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
