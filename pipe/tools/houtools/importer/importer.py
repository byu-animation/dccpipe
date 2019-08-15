import hou, sys, os, json

from pipe.am.project import Project
from pipe.am.environment import Department, Environment
from pipe.am.element import Element
from pipe.am.body import Body, Asset, Shot, AssetType
from pipe.tools.houtools.assembler.assembler import Assembler
from pipe.tools.houtools.cloner.cloner import Cloner
from pipe.tools.houtools.utils.utils import *
import pipe.gui.quick_dialogs as qd
import pipe.gui.select_from_list as sfl


class Importer:

    def __init__(self):
        self.select_from_list_dialog = None

    def run(self):
        project = Project()
        list = project.list_assets()

        shot_list = []

        for item in list:
            asset = project.get_asset(item)
            if asset.get_type() == AssetType.SHOT:
                shot_list.append(item)

        print("shot list: ", shot_list)

        self.select_from_list_dialog = sfl.SelectFromList(l=shot_list, parent=houdini_main_window(), title="Select a shot to import")
        self.select_from_list_dialog.submitted.connect(self.import_shot)

    def import_shot(self, shot_name):
        shot_name = shot_name[0]

        # Bring in the body so we can get info
        body = Project().get_body(shot_name)
        if not body:
            qd.error("Error with body.")
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
        characters_json = []
        animated_props_json = []

        # open the json files for sets characters and animated props
        try:
            with open(os.path.join(cache_dir, "sets.json")) as f:
                sets_json = json.load(f)
        except Exception as error:
            print "{0}/sets.json not found.".format(cache_dir)

        try:
            with open(os.path.join(cache_dir, "characters.json")) as f:
                characters_json = json.load(f)
        except Exception as error:
            print "{0}/characters.json not found.".format(cache_dir)

        try:
            with open(os.path.join(cache_dir, "animated_props.json")) as f:
                animated_props_json = json.load(f)
        except Exception as error:
            print "{0}/animated_props.json not found.".format(cache_dir)

        set_nodes = []
        character_nodes = []
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

        print("Loading characters: ")
        for character in characters_json:
            print("Character: ", character)

            if character["asset_name"] == "dcc_camera":
                camera_node = self.tab_in_camera(shot_name)
                character_nodes.append(camera_node)
                continue

            try:
                # get the most recent data for this reference
                asset_name = character["asset_name"]
                character_node, instances = Cloner().asset_results([asset_name])
                # Assembler().update_contents_character(character_node, asset_name, shot=shot_name)

                # character_node = cloned_subnet.copyTo(inside)
                # cloned_subnet.destroy()
                # character_node = Assembler().dcc_character(hou.node("/obj"), character["asset_name"],shot=shot_name)

                # TODO: add the shot name in the dcc_geo inside dcc_character
                inside = character_node.node("inside")
                geo = inside.node("geo")
                geo.parm("version_number").setExpression("ch(\"../../version_number\")", language=hou.exprLanguage.Hscript)
                geo.parm("space").set("anim")
                geo.parm("asset_department").set("rig")
                geo.parm("shot").set(shot_name)

                character_nodes.append(character_node)
            except:
                print "Error with {0}".format(character)
                continue
            #shot_parm = character_node.parm("shot")
            #shot_parm.set(shot_name)

            data_parm = character_node.parm("data")
            data = data_parm.evalAsJSONMap()
            data["version_number"] = str(character["version_number"])
            data_parm.set(data)

            version_number_parm = character_node.parm("version_number")
            version_number_parm.set(character["version_number"])

        # create network box in houdini and fill it with all objects in the shot
        box = hou.node("/obj").createNetworkBox()
        box.setComment(shot_name)
        for set_node in set_nodes:
            box.addItem(set_node)
        for character_node in character_nodes:
            box.addItem(character_node)
        for animated_prop_node in animated_prop_nodes:
            box.addItem(animated_prop_node)

        # move all the imported objects to a non-overlaid position in the node editor
        for set_node in set_nodes:
            set_node.moveToGoodPosition()
        for character_node in character_nodes:
            character_node.moveToGoodPosition()
        for animated_prop_node in animated_prop_nodes:
            character_node.moveToGoodPosition()

    def tab_in_camera(self, shot_name):
        camera_node = hou.node("/obj").createNode("dcc_camera")
        camera_node.parm("shot").set(shot_name)
        return camera_node
