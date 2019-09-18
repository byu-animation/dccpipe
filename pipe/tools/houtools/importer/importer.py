import hou, sys, os, json

from pipe.am.project import Project
from pipe.am.environment import Department, Environment
from pipe.am.element import Element
from pipe.am.body import Body, Asset, Shot, AssetType
from pipe.tools.houtools.assembler.assembler import Assembler
from pipe.tools.houtools.utils.utils import *
import pipe.gui.quick_dialogs as qd
import pipe.gui.select_from_list as sfl


class Importer:

    def __init__(self):
        self.select_from_list_dialog = None

    def run(self):
        project = Project()
        shot_list = project.list_shots()
        print("shot list: ", shot_list)

        self.select_from_list_dialog = sfl.SelectFromList(l=shot_list, parent=houdini_main_window(), title="Select a shot to import")
        self.select_from_list_dialog.submitted.connect(self.import_shot)

    def import_shot(self, shot_name):
        shot_name = shot_name[0]

        # Bring in the body so we can get info
        body = Project().get_body(shot_name)
        print("shot name: ", shot_name)
        print("body: ", str(body))
        if not body:
            qd.error("Error with asset.")
            return
        elif not body.is_shot():
            qd.error("Body is not shot?")
            return

        # Bring in element so we can get cache directory
        element = body.get_element(Department.ANIM)
        if not element:
            qd.error("Anim department does not exist for {0} ".format(shot_name))
            return

        cache_dir = element.get_cache_dir()

        sets_json = []
        actors_json = []
        animated_props_json = []

        # open the json files for sets actors and animated props
        try:
            with open(os.path.join(cache_dir, "sets.json")) as f:
                sets_json = json.load(f)
        except Exception as error:
            print "{0}/sets.json not found.".format(cache_dir)

        try:
            with open(os.path.join(cache_dir, "actors.json")) as f:
                actors_json = json.load(f)
        except Exception as error:
            print "{0}/actors.json not found.".format(cache_dir)

        try:
            with open(os.path.join(cache_dir, "animated_props.json")) as f:
                animated_props_json = json.load(f)
        except Exception as error:
            print "{0}/animated_props.json not found.".format(cache_dir)

        set_nodes = []
        actor_nodes = []
        animated_prop_nodes = []

        print("Loading sets:")
        for set in sets_json:
            print("Set: ", set)

            try:
                set_node = Assembler().tab_in(hou.node("/obj"), set["asset_name"])
            except:
                print "Error with {0}".format(set)
                continue

            set_nodes.append(set_node)

            print("Loading props in set ", set)
            for prop in set_node.children():
                print("Prop: ", prop)
                data_parm = prop.parm("data")

                if data_parm is None:
                    continue

                data = data_parm.evalAsJSONMap()
                for animated_prop in animated_props_json:
                    if data["asset_name"] == animated_prop["asset_name"] and data["version_number"] == animated_prop["version_number"]:
                        prop.parm("space").set("anim")
                        prop.parm("shot").set(shot_name)
                        animated_prop_nodes.append(prop)

        print("Loading actors: ")
        for actor in actors_json:
            print("Actor: ", actor)

            if actor["asset_name"] == "dcc_camera":
                camera_node = self.tab_in_camera(shot_name)
                actor_nodes.append(camera_node)
                continue

            try:
                # get the most recent data for this reference
                asset_name = actor["asset_name"]

                try:
                    from pipe.tools.houtools.cloner.cloner import Cloner
                except:
                    pass

                actor_node, instances = Cloner().asset_results([asset_name])
                # Assembler().update_contents_actor(actor_node, asset_name, shot=shot_name)

                # actor_node = cloned_subnet.copyTo(inside)
                # cloned_subnet.destroy()
                # actor_node = Assembler().dcc_actor(hou.node("/obj"), actor["asset_name"],shot=shot_name)

                # TODO: add the shot name in the dcc_geo inside dcc_actor
                inside = actor_node.node("inside")
                geo = inside.node("geo")
                geo.parm("version_number").setExpression("ch(\"../../version_number\")", language=hou.exprLanguage.Hscript)
                geo.parm("space").set("anim")
                geo.parm("asset_department").set("rig")
                geo.parm("shot").set(shot_name)

                actor_nodes.append(actor_node)
            except:
                print "Error with {0}".format(actor)
                continue
            #shot_parm = actor_node.parm("shot")
            #shot_parm.set(shot_name)

            data_parm = actor_node.parm("data")
            data = data_parm.evalAsJSONMap()
            data["version_number"] = str(actor["version_number"])
            data_parm.set(data)

            version_number_parm = actor_node.parm("version_number")
            version_number_parm.set(actor["version_number"])

        cam_dir = body.get_element(Department.CAMERA).get_cache_dir()
        camera_files = os.listdir(cam_dir)
        cameras = []

        for camera_file in camera_files:
            cameras.append( self.tab_in_camera(str(shot_name), str(camera_file)) )

        # create network box in houdini and fill it with all objects in the shot
        box = hou.node("/obj").createNetworkBox()
        box.setComment(shot_name)
        for set_node in set_nodes:
            box.addItem(set_node)
        for actor_node in actor_nodes:
            box.addItem(actor_node)
        for animated_prop_node in animated_prop_nodes:
            box.addItem(animated_prop_node)
        for camera in cameras:
            box.addItem(camera)

        # move all the imported objects to a non-overlaid position in the node editor
        for set_node in set_nodes:
            set_node.moveToGoodPosition()
        for actor_node in actor_nodes:
            actor_node.moveToGoodPosition()
        for animated_prop_node in animated_prop_nodes:
            actor_node.moveToGoodPosition()

        layout_object_level_nodes()

    def tab_in_camera(self, shot_name, camera_file):
        camera_node = hou.node("/obj").createNode("dcc_camera")
        camera_node.parm("shot").set(shot_name)
        camera_node.parm("cam").set(camera_file)
        return camera_node
