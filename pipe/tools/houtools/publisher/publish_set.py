import hou
import os
import json
import numpy as np

from pipe.am.environment import Environment
from pipe.am import pipeline_io
from pipe.am.body import Body
from pipe.am.project import Project
from pipe.am.element import Element
import pipe.gui.quick_dialogs as qd
import pipe.gui.select_from_list as sfl
from pipe.tools.houtools.utils.utils import *




class publish_set():

    def set_results(self, value):
        set_name = value[0]
        project = Project()
        self.body = project.get_body(set_name)

        obj = hou.node("/obj")
        set = obj.node(set_name)

        if set is None:
            qd.error("No set found with that name. Please check naming and try again.")
            return

        #migrate transforms for all the children to set_dressing_transform
        self.update_set_dressing_transform(set)

        #create children list (list of houdini objects)
        print("set: ", set)
        inside = set.node("inside")
        children = inside.children()

        set_file = os.path.join(Project().get_assets_dir(), set_name, "model", "main", "cache", "whole_set.json")

        '''
        The idea here is to get the set data from whole_set.json,
        get the set data from Houdini, and then compare the two.
        Here are the possible scenarios:
            1. There are items in the JSON file that aren't in the Houdini Set
                -remove the item from the Json file
                -remove the item's json files
            2. There are items in the Houdini Set that aren't in the JSON file
                -Add those to the JSON file
        '''

        items_to_delete = []
        set_data = []
        items_in_set = []

        items_to_delete, set_data, items_in_set = self.get_set_comparable_lists(children, set_file)

        self.delete_asset_json(items_to_delete, set_name)

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

        print("starting to work on children\n")
        for child in children:

            #find if it is scaled (set to big scale) and initialize variables----------------------------------------------------------
            #inside
            #import_node
            #out
            #set_transform
            #current_version
            #name

            isScaled = False
            print("child: " + str(child))
            print("current set_data: " + str(set_data))
            if child.type().name() == "dcc_geo":
                inside = child.node("inside")
                import_node = child.node("import")
                if child.parm("Scale_Object").evalAsInt() == 1:
                    child.parm("Scale_Object").set(0)
                    isScaled = True
            else:
                inside = child.node("inside")
                geo = inside.node("geo")
                inside = geo.node("inside")
                import_node = geo.node("import")

            out = inside.node("OUT")
            set_transform = inside.node("set_dressing_transform")
            current_version = child.parm("version_number").evalAsInt()
            #need a asset number or letter (I honestly just need to name it something and have that reflected in houdini)
            #import_number = child.parm("import_number").evalAsInt

            name = child.parm("asset_name").evalAsString()

            #---------------------------------------------------------------------------------------------------------------------------

            child_body = project.get_body(name)
            if child_body is None:
                qd.warning(str(name) + " not found in pipe. Please check that node is named correctly.")
                continue

            cache_dir = os.path.join(Project().get_assets_dir(), set_name, "model", "main", "cache")
            print("filepath: ", cache_dir)
            latest_version, version_string = self.body.version_prop_json(name, cache_dir)
            print('latest version: ', latest_version)
            new_version = latest_version
            latest_version -= 1

            prop_file = os.path.join(cache_dir, str(name) + "_" + str(current_version) + ".json")
            print("prop file: ", prop_file)

            #will have to change items_in_set to be checked
            if name in items_in_set:
                print("set contains asset: " + str(name))
                try:
                    with open(prop_file) as f:
                        prop_data = json.load(f)
                except Exception as error:
                    print("No valid JSON file for " + str(name) + ". Skipping changes made to this asset.")
                    continue

                for set_item in set_data:
                    if str(set_item['asset_name']) == str(name):
                        if set_item['version_number'] <= current_version:
                            print("updating ", set_item, " with version ", new_version)
                            set_item['version_number'] = new_version
                            break

            else:
                # create blank prop data and add it to the set
                print(str(name) + " not found in set file.")
                path = self.get_prim_path(out)
                prop_data = {"asset_name": name, "version_number": 0, "path" : str(path), "a" : [0, 0, 0], "b" : [0, 0, 0], "c" : [0, 0, 0] }
                set_data.append({"asset_name": str(name), "version_number": 0})
                print("appended set_data: " + str(set_data))
                new_version = 0
                items_in_set.append(name)

            print("current set_data: " + str(set_data))

            new_prop_file = os.path.join(Project().get_assets_dir(), set_name, "model", "main", "cache", str(name) + "_" + str(new_version) + ".json")

            # get a b and c from prop_data file. Each is an array of size 3, representing x,y,z coords
            a = prop_data['a']
            b = prop_data['b']
            c = prop_data['c']

            self.update_points_by_geo(out, prop_data['path'], a, b, c)

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
            print("")

            self.clear_transform(set_transform)
            self.set_space(child, set_name, name, new_version)

            if isScaled:
                child.parm("Scale_Object").set(1)

        #reloading the new data that was written
        try:
            read_from_json = import_node.node("read_from_json")
            read_from_json.parm("reload").pressButton()
        except:
            print("no nodes are in the set, cannot read from JSON")

        #rewriting the whole_set json file
        outfile = open(set_file, "w")
        print("set data: ", set_data)
        updated_set_data = json.dumps(set_data)
        outfile.write(updated_set_data)
        outfile.close()

        qd.info("Set " + str(set_name) + " published successfully!")

    def get_set_comparable_lists(self, children, set_file):
        set_data = []
        try:
            with open(set_file) as f:
                set_data = json.load(f)
        except Exception as error:
            qd.error("No valid JSON file for " + str(set_name))
            return
        print("SET_DATA FROM JSON: " + str(set_data))


        #create the list of asset names from the json file (list of strings)
        items_in_set = []
        items_in_set = [item['asset_name'] for item in set_data];
        print("Items in set from JSON: " + str(items_in_set))

        #create the list of asset names from the current houdini's set (list of strings)
        child_names = []
        child_names = [child.parm('asset_name').eval() for child in children]
        print("Items IN HOUDINI: " + str(children))
        print("Asset Names:" + str(child_names))


        #edit lists to only contain items that were explicitly in the set in Houdini
        #create the list of assets to delete (dictionary of asset_name and version_number)
        items_to_delete = []
        items_to_delete[:] = [{'asset_name': item['asset_name'], 'version_number': item['version_number']} for item in set_data if str(item['asset_name']) not in child_names]
        print("items deleted in set: " + str(items_to_delete))

        #edit set_data to include only objects (asset_name, version_number) that are still found in the set
        #note: it won't include anything in the scene that wasn't origionally in the json file
        set_data[:] = [item for item in set_data if str(item['asset_name']) in child_names]
        print("new set data: " + str(set_data))

        #edit doing the same thing as above except its only the asset name thats being saved this time
        items_in_set[:] = [item['asset_name'] for item in set_data if str(item['asset_name']) in child_names]
        print("new items in set: " + str(items_in_set))

        return items_to_delete, set_data, items_in_set

    def delete_asset_json(self, items_to_delete, set_name):
        print("deleting asset")
        set_file_dir = os.path.join(Project().get_assets_dir(), set_name, "model", "main", "cache")
        delete_dir = "backup"
        print(set_file_dir)
        if not os.path.isdir(os.path.join(set_file_dir, delete_dir)):
            os.makedirs(os.path.join(set_file_dir, delete_dir))
        for item in items_to_delete:
            for ver_num in range(int(item['version_number']) + 1):
                file_name = str(item['asset_name']) + '_' + str(ver_num) + '.json'
                old_abs_path = os.path.join(set_file_dir, file_name)
                new_abs_path = os.path.join(set_file_dir, delete_dir, file_name)
                print('moving: ' + file_name + ' to ' + os.path.join(delete_dir, file_name))
                print(old_abs_path)
                print(new_abs_path)
                #need to put this in a try catch block to avoid unnamed asset errors
                try:
                    os.rename(old_abs_path, new_abs_path)
                except:
                    print(old_abs_path + ' file doesn\t exist')

    def get_path_point_starting_num(self, geo, path):
        starting_point = None
        found = False
        for point in geo.points():
            for prim in point.prims():
                if str(path) in str(prim.attribValue("path")):
                    starting_point = point
                    found = True
                    break
            if found is True:
                break
        if not starting_point:
            qd.warning("Could not find the correct path for " + str(path) + ". Transform may be incorrect.")
            start_num = 0
        else:
            print("start point: ", starting_point)
            start_num = starting_point.number()
        return start_num

    def get_points_from_path(self, geo, point_num, num_points = 3):
        pointList = []
        for i in range(num_points):
            pointList.append(geo.iterPoints()[point_num + i])
        return pointList;

    def get_position_from_point(self, point):
        return point.position()[0], point.position()[1], point.position()[2]

    def get_prim_path(self, out):
        geo = out.geometry()
        try:
            pathList = geo.findPrimAttrib("path").strings()
        except:
            print("path attribute doesn't exist on object (error in update_points_by_geo)")
            return
        for path in pathList:
            start_num = self.get_path_point_starting_num(geo, path)

            point_a, point_b, point_c = self.get_points_from_path(geo, start_num, 3)

            a_x, a_y, a_z = self.get_position_from_point(point_a)
            b_x, b_y, b_z = self.get_position_from_point(point_b)
            c_x, c_y, c_z = self.get_position_from_point(point_c)

            c_a = np.array([c_x - a_x, c_y - a_y, c_z - a_z])
            b_a = np.array([b_x - a_x, b_y - a_y, b_z - a_z])

            c_a_norm = np.linalg.norm(c_a)
            b_a_norm = np.linalg.norm(b_a)

            if not np.array_equal(c_a/c_a_norm, b_a/b_a_norm) and not np.array_equal(c_a/c_a_norm, -1 * b_a/b_a_norm):
                break;
            print(path + '\'s first 3 points are in a line')
        return path

    def update_points_by_geo(self, out, path, a, b, c):

        geo = out.geometry()
        print("Updating points by geo:")
        print("Out is " + str(out))
        print("path: " + str(path))
        print("a: " + str(a))
        print("b: " + str(b))
        print("c: " + str(c))

        start_num = self.get_path_point_starting_num(geo, path)

        point_a, point_b, point_c = self.get_points_from_path(geo, start_num, 3)

        a_x, a_y, a_z = self.get_position_from_point(point_a)
        b_x, b_y, b_z = self.get_position_from_point(point_b)
        c_x, c_y, c_z = self.get_position_from_point(point_c)

        a[0] = a_x
        a[1] = a_y
        a[2] = a_z
        b[0] = b_x
        b[1] = b_y
        b[2] = b_z
        c[0] = c_x
        c[1] = c_y
        c[2] = c_z

    def get_full_transform(self, child):
        try:
            tx = child.parm("tx").evalAsFloat()
            ty = child.parm("ty").evalAsFloat()
            tz = child.parm("tz").evalAsFloat()
            rx = child.parm("rx").evalAsFloat()
            ry = child.parm("ry").evalAsFloat()
            rz = child.parm("rz").evalAsFloat()
            sx = child.parm("sx").evalAsFloat()
            sy = child.parm("sy").evalAsFloat()
            sz = child.parm("sz").evalAsFloat()
            px = child.parm("px").evalAsFloat()
            py = child.parm("py").evalAsFloat()
            pz = child.parm("pz").evalAsFloat()
            scale = child.parm("scale").evalAsFloat()

            return tx, ty, tz, rx, ry, rz, sx, sy, sz, px, py, pz, scale
        except:
            print("ERROR OCCURRED IN GET_FULL_TRANSFORM: " + str(child) + " had an issue with transforms")
            return 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0, 1.0, 1.0, 0.0, 0.0, 0.0, 1.0

    def set_space(self, child, set_name, child_name, version_number):
        if child.type().name() == "dcc_geo":
            child.parm("space").set("set")
            child.parm("space").eval()
            child.parm("set").set(set_name)
            child.parm("set").eval()

        child.parm("asset_name").set(child_name)
        child.parm("asset_name").eval()
        child.parm("version_number").set(version_number)
        child.parm("version_number").eval()

    def clear_transform(self, child):
        parm_scale_list = ["sx", "sy", "sz", "scale"]
        parm_list = ["tx", "ty", "tz", "rx", "ry", "rz", "sx", "sy", "sz", "scale"]

        for parm in parm_list:
            if parm not in parm_scale_list:
                child.parm(parm).set(0.0)
            else:
                child.parm(parm).set(1.0)
            child.parm(parm).eval()

    def update_set_dressing_transform(self, setNode):
        print("Updating set_dressing_transform....")
        print(setNode)
        insideNode = setNode.children()
        setNode = insideNode[0]
        propNodes = setNode.children()
        print("Path to Set: " + str(setNode.path()))
        print("Nodes inside the set: " + str(propNodes))
        for geo in propNodes:
            tx, ty, tz, rx, ry, rz, sx, sy, sz, px, py, pz, scale = self.get_full_transform(geo)

            scaleValue = 1.0
            if geo.parm("Scale_Object").evalAsInt() == 1:
                try:
                    scaleValue = 1.0/geo.node("Scale_object_transform").parm("scale").eval()
                except:
                    print("ERROR: Scale value might be zero? Cannot divide by zero")
                    scaleValue = 1.0

            inside = geo.node("inside")
            transformNode = inside.node("set_dressing_transform")

            old_tx, old_ty, old_tz, old_rx, old_ry, old_rz, old_sx, old_sy, old_sz, old_px, old_py, old_pz, old_scale = self.get_full_transform(transformNode)
            old_sx -= 1.0
            old_sy -= 1.0
            old_sz -= 1.0
            old_scale -= 1.0

            transformNode.parm("tx").set(tx*scaleValue + old_tx)
            transformNode.parm("ty").set(ty*scaleValue + old_ty)
            transformNode.parm("tz").set(tz*scaleValue + old_tz)
            transformNode.parm("rx").set(rx + old_rx)
            transformNode.parm("ry").set(ry + old_ry)
            transformNode.parm("rz").set(rz + old_rz)
            transformNode.parm("sx").set(sx + old_sx)
            transformNode.parm("sy").set(sy + old_sy)
            transformNode.parm("sz").set(sz + old_sz)
            transformNode.parm("px").set(px*scaleValue + old_px)
            transformNode.parm("py").set(py*scaleValue + old_py)
            transformNode.parm("pz").set(pz*scaleValue + old_pz)
            transformNode.parm("scale").set(scale + old_scale)

            self.clear_transform(geo)
