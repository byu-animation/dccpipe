'''
    Big thanks to Hunter Tinney for creating most of the v2 HDAs
    ================
    Intro to Pipe V2
    ================
    I designed this new procedure to minimize dependencies and allow for easier changes to our Houdini pipeline. With the old
    code, whenever we assembled an asset, we were locked into a specific configuration for that asset and would need to
    re-assemble if anything changed. Now, we abstracted out a lot of the functionality into nodes like DCC Import, DCC Geo,
    DCC Character, DCC Set, etc, so that way we push changes to all the assets at once (for example, if we were to switch to
    USD mid production.)
    Please pay attention to the differences in each of these nodes. Functional HDAs and Template HDAs are very different (for
    example, a Template HDA is never intended to be tabbed into Houdini, it simply serves as a template for creating other
    HDAs.)
    =======================
    Dynamic Content Subnets
    =======================
    These HDAs are simply subnets that hold other HDAs. The difference is that they will destroy and re-tab in the HDAs inside
    of them, based on what asset is loaded. Let's say Swingset_001 is loaded, and we switch to Swingset_002. DCC Geo would
    switch out all the Content HDAs (material, etc.) of Swingset_001 with the content of Swingset_002. A description of
    Content HDAs is found in the "Content HDAs" section.
        NAME         Subnet Type    Description
     ----------------------------------------------------------------------------------------------------------------------------
    | DCC Geo          OBJ>SOP    Houses the other nodes at the most basic level, good enough for props and character meshs.     |
    | DCC Character    OBJ>OBJ    Houses a DCC Geo, a Hair asset and a Cloth asset. It's our verion of a character group.        |
    | DCC Set          OBJ>OBJ    Reads from a JSON file (exported from Maya) that contains positions of assets in a set. It     |
    |                                 tabs them all in as DCC Geos, and then offsets them to their correct                       |
    |                                 positions/scales/rotates.                                                                  |
     ----------------------------------------------------------------------------------------------------------------------------
    ===============
    Functional HDAs
    ===============
    These HDAs take some of the more common procedures and generalize them. That way, if we ever change the way we import
    geometry into Houdini, we could make a simple change to DCC Import (for example) and that change would propagate to all
    the assets that contain DCC Import.
        NAME         Node Type    Description
     ----------------------------------------------------------------------------------------------------------------------------
    | DCC Import       SOP        Has all the functionality to bring in assets from the pipe via Alembic. This functionality     |
    |                                 could be swapped out for USD Import at a future date.                                      |
    | DCC Mat. Assign  SOP        Full Name: DCC Material Assign. Basically the Material SOP, but provides a way of switching    |
    |                                 between material options.                                                                  |
    | DCC Shopnet      SOP        Provides a way for us to supply default material setups for shading artists.                   |
    | DCC Primvars     SOP        Allows for quick selection of primitive/point/vertex groups and using them as masks for        |
    |                                 RenderMan shaders.                                                                         |
     ----------------------------------------------------------------------------------------------------------------------------
    =============
    Template HDAs
    =============
    These HDAs will never be tabbed in directly. They simply serve as template data that can be used to create other HDAs. Please
    see the section on "Content HDAs" below for an explanation of the process.
        NAME         Node Type    Description
     ----------------------------------------------------------------------------------------------------------------------------
    | DCC Material     SOP         Holds a Primvars, Mat. Assign and Shopnet Functional HDA. Intended for shading.                |
    | DCC Modify       SOP         Modifies incoming geometry, intended for any geometry fixes that need to be done in Houdini.   |
    | DCC Hair         OBJ>OBJ     Holds all hair subnets for a given character. It should take a DCC Geo as an input. It should  |
    |                                  also have simulation parameters promoted to the top-level, which is done by the artist.    |
    | DCC Cloth        OBJ>OBJ     Holds all cloth subnets for a given character. It should take a DCC Geo as an input. It should |
    |                                  also have simulation parameters promoted to the top-level, which is done by the artist.    |
     ----------------------------------------------------------------------------------------------------------------------------
    ============
    Content HDAs
    ============
    Content HDAs are simply instances of Template HDAs. They could be materials, modify nodes, hair subnets, cloth subnets, etc.
    Typically their names will be something like "swingset_001_material". These HDAs are created on an as-needed basis for
    each asset in the pipe (although most assets will have a material.) They are created by duplicating the Template HDA
    (which is stored in the houdini-tools package.) We store that HDA in the User folder of the artist. Then, when they are ready,
    we publish it to the pipe as a new HDA. Because it is a new HDA definition, we are locked into its functionality unless the
    asset is re-created. This is a bit unfortunate (it is the equivalent to copying and pasting similar code instead of abstracting
    it out into a shared function/class.) However, we have ensured that most of the functionality that we would like to tweak has
    been abstracted out into Functional HDAs that are inside each of these nodes. That way, if we change the functional HDAs, we
    will propagate those changes to all the Content HDAs that contain them. If you find a better way to emulate polymorphism in
    HDAs, please update this!!
    ========
    Updating
    ========
    The different update modes have different meanings.
        smart: Sets will add new components, and delete old ones. Props and characters will update everything except checked out items and shot_modeling.
        clean: Everything is deleted and re-tabbed in, ensuring it is 100% synced. Does not allow for overrides.
        frozen: Nothing happens.
'''


import hou, sys, os, json
from pipe.am.project import Project
from pipe.am.environment import Environment, Department
from pipe.am.element import Element
from pipe.am.body import Body, Asset, Shot, AssetType

import pipe.gui.select_from_list as sfl
import pipe.gui.quick_dialogs as qd
import pipe.gui.write_message as wm

from pipe.tools.houtools.utils.utils import *
from pipe.tools.houtools.publisher.publisher import Publisher
try:
    from pipe.tools.houtools.cloner.cloner import Cloner
except:
    print("Cloner already loaded. Skipping.")


class UpdateModes:
    SMART = "smart"
    CLEAN = "clean"
    FROZEN = "frozen"

    @classmethod
    def list_modes(cls):
        return [cls.SMART, cls.CLEAN, cls.FROZEN]

    @classmethod
    def mode_from_index(cls, index):
        return [cls.SMART, cls.CLEAN, cls.FROZEN][index]


class Assembler:
    def __init__(self):
        self.asset_gui = None

        # The order in which these nodes appear is the order they will be created in
        self.dcc_geo_departments = [Department.MODIFY, Department.MATERIAL]
        self.dcc_character_departments = [Department.HAIR, Department.CLOTH]
        self.all_departments = [Department.MODIFY, Department.MATERIAL, Department.HAIR, Department.CLOTH]

        # The source HDA's are currently stored inside the pipe source code.
        self.hda_path = Environment().get_otl_dir()

        # We define the template HDAs definitions here, for use in the methods below
        self.hda_definitions = {
            Department.MATERIAL: hou.hdaDefinition(hou.sopNodeTypeCategory(), "dcc_material", os.path.join(self.hda_path, "dcc_material.hda")),
            Department.MODIFY: hou.hdaDefinition(hou.sopNodeTypeCategory(), "dcc_modify", os.path.join(self.hda_path, "dcc_modify.hda")),
            Department.HAIR: hou.hdaDefinition(hou.objNodeTypeCategory(), "dcc_hair", os.path.join(self.hda_path, "dcc_hair.hda")),
            Department.CLOTH: hou.hdaDefinition(hou.objNodeTypeCategory(), "dcc_cloth", os.path.join(self.hda_path, "dcc_cloth.hda"))
        }

        # By default, we ignore "Asset Controls", so that we can put things in there without them being promoted.
        # See: inherit_parameters() method
        self.default_ignored_folders = ["Asset Controls"]

    def run(self):
        # step 1: Select the body
        # step 2: assemble the element

        project = Project()
        asset_list = project.list_assets()

        non_shot_list = []

        for item in asset_list:
            asset = project.get_asset(item)
            if not asset.get_type() == AssetType.SHOT:
                non_shot_list.append(item)

        self.asset_gui = sfl.SelectFromList(l=non_shot_list, parent=houdini_main_window(), title="Select a prop, character, or set to assemble")
        self.asset_gui.submitted.connect(self.asset_results)

    def asset_results(self, asset):
        self.selected_asset = asset[0]

        project = Project()
        self.body = project.get_body(self.selected_asset)

        parent, instances = self.create_hda(self.selected_asset)

        # layout all /obj level nodes so none are stacked
        node = hou.node("/obj")
        node.layoutChildren()

        print("created ", instances, " in ", parent)

    '''
        Easily callable method, meant for tool scripts
    '''
    def tab_in(self, parent, asset_name, already_tabbed_in_node=None, excluded_departments=[]):
        print "Creating node for {0}".format(asset_name)
        body = Project().get_body(asset_name)
        if body is None or not body.is_asset():
            qd.error("Pipeline error: This asset either doesn't exist or isn't an asset.")
            return
        if body.get_type() == AssetType.CHARACTER:
            return self.dcc_character(parent, asset_name, already_tabbed_in_node, excluded_departments)
        elif body.get_type() == AssetType.PROP:
            return self.dcc_geo(parent, asset_name, already_tabbed_in_node, excluded_departments)
        elif body.get_type() == AssetType.SET:
            return self.dcc_set(parent, asset_name, already_tabbed_in_node)
        else:
            qd.error("Pipeline error: this asset isn't a character, prop or set.")
            return

    '''
        Easily callable method, meant for tool scripts
    '''
    def update_contents(self, node, asset_name, mode=UpdateModes.SMART):
        if node.type().name() == "dcc_set":
            self.update_contents_set(node, asset_name, mode=mode)
        elif node.type().name() == "dcc_character":
            self.update_contents_character(node, asset_name, mode=mode)
        elif node.type().name() == "dcc_geo":
            self.update_contents_geo(node, asset_name, mode=mode)

    def subnet_type(self, asset_name):
        body = Project().get_body(asset_name)
        if body is None or not body.is_asset():
            qd.error("Pipeline error: This asset either doesn't exist or isn't an asset.")
            return
        if body.get_type() == AssetType.CHARACTER:
            return "dcc_character"
        elif body.get_type() == AssetType.PROP:
            return "dcc_geo"
        elif body.get_type() == AssetType.SET:
            return "dcc_set"
        else:
            qd.error("Pipeline error: this asset isn't a character, prop or set.")
            return



    '''
        This function tabs in a DCC Set and fills its contents with other DCC Geo nodes based on JSON data
    '''

    def dcc_set(self, parent, set_name, already_tabbed_in_node=False, mode=UpdateModes.CLEAN):

        # Check if it's a set and that it exists
        body = Project().get_body(set_name)
        if not body.is_asset() or not body.get_type() == AssetType.SET:
            qd.error("Must be a set.")

        node = already_tabbed_in_node if already_tabbed_in_node else parent.createNode("dcc_set")
        try:
            node.setName(set_name)
        except:
            node.setName(set_name + "_1", unique_name=True)
        # Update contents in the set
        self.update_contents_set(node, set_name, mode)
        return node


    # Utility function to find if a node's asset and version number match an entry in the set's JSON
    def matches_reference(self, child, reference):

        # Grab data off the node. This data is stored as a key-value map parameter
        data = child.parm("data").evalAsJSONMap()

        print "{0}:\n\t checked {1} against {2}".format(str(child), str(data), str(reference))

        # If it matches both the asset_name and version_number, it's a valid entry in the list
        if data["asset_name"] == reference["asset_name"] and data["version_number"] == str(reference["version_number"]):
            print "\tand it matched"
            return True
        else:
            print "\tand it didn't match"
            return False

    '''
        Updates the contents of a set
    '''
    def update_contents_set(self, node, set_name, mode=UpdateModes.SMART):
        # TODO: instead of tabbing in the contents of the json, we need to run it through create_hda (like cloner does) to get the more recent versions
        # TODO: in fact, we can just call clone for each asset inside to get the more recent versions. That, or abstract the functionality out to utils
        # TODO: Also, we need to create a template HDA for dcc_assembly that we can use to store the vertex positions (or something)
        # TODO: Actually, we'll try to just use the JSON file to store translated positions

        # Check if reference file exists
        set_file = os.path.join(Project().get_assets_dir(), set_name, "model", "main", "cache", "whole_set.json")

        # Error checking
        try:
            with open(set_file) as f:
                set_data = json.load(f)
        except Exception as error:
            qd.error("No valid JSON file for " + set_name)
            return

        node.parm("asset_name").set(set_name)
        data = node.parm("data").evalAsJSONMap()
        data["asset_name"] = set_name
        node.parm("data").set(data)
        inside = node.node("inside")

        # Grab current DCC Dynamic Content Subnets that have been tabbed in
        current_children = [child for child in inside.children() if child.type().name() in ["dcc_set", "dcc_character", "dcc_geo"]]

        # Smart updating will only destroy assets that no longer exist in the Set's JSON list
        if mode == UpdateModes.SMART:
            non_matching = [child for child in current_children if len([reference for reference in set_data if matches_reference(child, reference)]) == 0]
            for non_match in non_matching:
                non_match.destroy()

        # Clean updating will destroy all children.
        elif mode == UpdateModes.CLEAN:
            inside.deleteItems(inside.children())

        # Grab current children again
        current_children = [child for child in inside.children() if child.type().name() in ["dcc_set", "dcc_character", "dcc_geo"]]

        # Tab-in/update all assets in list
        for reference in set_data:
            body = Project().get_body(reference["asset_name"])

            if body is None:
                print 'Error on: ', reference["asset_name"]
                continue
            if not body.is_asset() or body.get_type() == AssetType.SET:
                continue

            # get the most recent data for this reference
            cloned_subnet, instances = Cloner().asset_results([reference["asset_name"]])

            # move the cloned asset inside the set node and delete the one on the top level
            subnet = cloned_subnet.copyTo(inside)
            cloned_subnet.destroy()

            # Try to not override parameters in the set
            if mode == UpdateModes.SMART:
                for key in reference:
                    # Pull parm from node
                    parm = subnet.parm(key)
                    # If a non-default value is there, it most likely came from a user. Don't overwrite it.
                    if parm and parm.isAtDefault():
                        parm.set(reference[key])

            # Override parameters in the set
            elif mode == UpdateModes.CLEAN:
                newparms = {"asset_name" : reference["asset_name"], "version_number" : reference["version_number"] }
                subnet.setParms(newparms)

            # Build the set accordingly
            subnet.parm("space").set("set")
            subnet.parm("set").set(set_name)
            subnet.parm("update_mode").set(UpdateModes.list_modes().index(mode))
            # Set the data
            subnet.parm("data").set({
                "asset_name": str(reference["asset_name"]),
                "version_number" : str(reference["version_number"])
            })

        inside.layoutChildren()

    '''
        Cache all the contents of the set for faster cooking
    '''
    def set_cache_path(self, parent, child):
        data = child.parm("data").evalAsJSONMap()
        cachepath = parent.parm("cachepath").evalAsString() + "/" + child.name()
        child.parm("cachepath").set(cachepath)

    def set_read_from_disk(self, node, on_or_off):
        inside = node.node("inside")
        children = [child for child in inside.children() if child.type().name() == "dcc_geo"]

        for child in children:
            set_cache_path(node, child)
            child.parm("read_from_disk").set(on_or_off)

    def reload_from_disk(self, node):
        inside = node.node("inside")
        children = [child for child in inside.children() if child.type().name() == "dcc_geo"]

        for child in children:
            set_cache_path(node, child)
            child.parm("reload_from_disk").pressButton()

    def save_to_disk(self, node):
        inside = node.node("inside")
        children = [child for child in inside.children() if child.type().name() == "dcc_geo"]

        for child in children:
            set_cache_path(node, child)
            read_from_disk_value = child.parm("read_from_disk").evalAsInt()
            child.parm("read_from_disk").set(0)
            child.parm("save_to_disk").pressButton()
            child.parm("read_from_disk").set(read_from_disk_value)


    '''
        This function tabs in a DCC Character node and fills its contents with the appropriate character name.
        Departments is a mask because sometimes we tab this asset in when we want to work on Hair or Cloth, and don't want the old ones to be there.
    '''
    def dcc_character(self, parent, asset_name, already_tabbed_in_node=None, excluded_departments=[], mode=UpdateModes.CLEAN, shot=None):

        # Set up the body/elements and make sure it's a character
        body = Project().get_body(asset_name)
        if not body.is_asset() or not body.get_type() == AssetType.CHARACTER:
            qd.error("Must be a character.")
            return None

        # If there's an already tabbed in node, set it to that node
        node = already_tabbed_in_node if already_tabbed_in_node else parent.createNode("dcc_character")
        try:
            node.setName(asset_name.title())
        except:
            node.setName(asset_name.title() + "_1", unique_name=True)
        node.parm("asset_name").set(asset_name)

        # Set the asset_name data tag
        data = node.parm("data").evalAsJSONMap()
        data["asset_name"] = asset_name
        node.parm("data").set(data)

        # Set the contents to the character's nodes
        self.update_contents_character(node, asset_name, excluded_departments, mode, shot)
        return node

    '''
        This function sets the inner contents of a DCC Character node.
    '''
    def update_contents_character(self, node, asset_name, excluded_departments=[], mode=UpdateModes.SMART, shot=None):

        # Set up the body/elements and make sure it's a character. Just do some simple error checking.
        body = Project().get_body(asset_name)
        if not body.is_asset() or body.get_type() != AssetType.CHARACTER or "dcc_character" not in node.type().name():
            qd.error("Must be a character.")
            return None

        # Reset the data parm
        data = node.parm("data").evalAsJSONMap()
        data["asset_name"] = asset_name
        node.parm("data").set(data)

        inside = node.node("inside")

        # Make sure the geo is set correctly
        geo = inside.node("geo")
        if geo is not None:
            if mode == UpdateModes.SMART:
                self.update_contents_geo(geo, asset_name, excluded_departments, mode)

            elif mode == UpdateModes.CLEAN:
                geo.destroy()
                geo = self.dcc_geo(inside, asset_name, excluded_departments=excluded_departments, character=True)
        else:
            geo = self.dcc_geo(inside, asset_name, excluded_departments=excluded_departments, character=True)

        # Tab in each content HDA based on department
        for department in self.dcc_character_departments:
            # If the department is not excluded, tab-in/update the content node like normal
            if department not in excluded_departments:

                self.update_content_node(node, inside, asset_name, department, mode)

            # If the department is excluded, we should delete it.
            elif mode == UpdateModes.CLEAN:

                self.destroy_if_there(inside, department)


        inside.layoutChildren()

        geo.parm("version_number").setExpression("ch(\"../../version_number\")", language=hou.exprLanguage.Hscript)

        # If this character is being animated, set parms accordingly
        if shot is not None:
            geo.parm("space").set("anim")
            geo.parm("asset_department").set("rig")
            geo.parm("shot").set(shot)

        return node

    '''
        This function tabs in a DCC Geo node and fills its contents according to the appropriate asset name.
    '''
    def dcc_geo(self, parent, asset_name, already_tabbed_in_node=None, excluded_departments=[], character=False, mode=UpdateModes.CLEAN):
        # Set up the body/elements and check if it's an asset.
        body = Project().get_body(asset_name)
        if not body.is_asset():
            qd.error("Must be an asset.")
            return None

        # Set up the nodes, name geo
        node = already_tabbed_in_node if already_tabbed_in_node else parent.createNode("dcc_geo")
        if character:
            node.setName("geo")
        else:
            try:
                node.setName(asset_name.title())
            except:
                node.setName(asset_name.title() + "_1", unique_name=True)

        # Set the asset_name data tag
        data = node.parm("data").evalAsJSONMap()
        data["asset_name"] = asset_name
        node.parm("data").set(data)

        # Set the contents to the nodes that belong to the asset
        self.update_contents_geo(node, asset_name, excluded_departments, mode)

        return node

    '''
        This function sets the dynamic inner contents of a DCC Geo node.
    '''
    def update_contents_geo(self, node, asset_name, excluded_departments=[], mode=UpdateModes.SMART):

        # Set up the body/elements and make sure it's not a character. Just do some simple error checking.
        body = Project().get_body(asset_name)
        if body is None:
            qd.error("Asset doesn't exist.")
            return None
        if not body.is_asset() or body.get_type() == AssetType.SET or "dcc_geo" not in node.type().name():
            qd.error("Must be a prop or character.")
            return None

        # Get interior nodes
        importnode = node.node("import")
        inside = node.node("inside")

        # Set the asset_name and reload
        if node.parm("asset_name").evalAsString() != asset_name:
            node.parm("asset_name").set(asset_name)
        importnode.parm("reload").pressButton()

        # Tab in each content HDA based on department
        for department in self.dcc_geo_departments:
            # If the department is not excluded, tab-in/update the content node like normal
            if department not in excluded_departments:
                self.update_content_node(node, inside, asset_name, department, mode, inherit_parameters = department == Department.MODIFY)

            # If the department is excluded, we should delete it.
            elif mode == UpdateModes.CLEAN:
                self.destroy_if_there(inside, department)

        inside.layoutChildren()

        return node

    def assemble_set(self, node):
        instances = []



        return instances

    '''
        Creates new content HDAs
        @param asset_name: name of the asset to assemble/clone
        @param department_paths: a dictionary of department to existing hda filepaths to clone. None if assembling
        @param already_tabbed_in_node: an hda where the new content hdas should be created. Typically None
    '''
    def create_hda(self, asset_name, body=None, department_paths=None, already_tabbed_in_node=None):
        if body is None:
            body = self.body

        type = self.check_body(body)

        if type is None:
            qd.error("Invalid body type specified.")
            return None

        # Tab in the parent asset that will hold this checked out HDA
        node = already_tabbed_in_node if already_tabbed_in_node else self.tab_in(hou.node("/obj"), asset_name) #, excluded_departments=[department])

        if type == AssetType.SET:
            return node, self.assemble_set(node)

        departments = self.get_departments(type)

        created_instances = []
        for department in departments:
            element = self.get_hda_element(body, department, asset_name)
            checkout_file = self.get_checkout_file(element)

            if department_paths:
                content_hda_filepath = department_paths[department]
            else:
                content_hda_filepath = None

            # CREATE NEW HDA DEFINITION
            self.create_new_hda_definition(element, asset_name, department, checkout_file, content_hda_filepath)

            # get the "inside" node definied in otls/dcc_inside.hda
            inside = self.get_inside_node(type, department, node)

            # Tab an instance of this new HDA into the asset you are working on
            hda_instance = self.assemble_hda_instance(asset_name, department, inside)
            created_instances.append(hda_instance)

        return node, created_instances

    '''
        Helper function for create_hda
    '''
    def check_body(self, body):
        # Check if this body is an asset. If not, return error.
        body = body
        if not body.is_asset():
            qd.error("Must be an asset of type PROP, CHARACTER or SET.")
            return None

        type = body.get_type()

        return type

    '''
        Helper function for create_hda
    '''
    def get_departments(self, type):
        if type == AssetType.CHARACTER:
            departments = self.all_departments
        elif type == AssetType.PROP:
            departments = self.dcc_geo_departments
        else:
            departments = self.dcc_geo_departments

        return departments

    '''
        Helper function for create_hda
    '''
    def get_hda_element(self, body, department, asset_name):
        # Create element if does not exist.
        element = body.get_element(department, name=Element.DEFAULT_NAME, force_create=True)
        element._datadict[Element.APP_EXT] = element.create_new_dict(Element.DEFAULT_NAME, department, asset_name)[Element.APP_EXT]
        element._update_pipeline_file()

        return element

    '''
        Helper function for create_hda
    '''
    def get_checkout_file(self, element):
        username = Project().get_current_username()
        checkout_file = element.checkout(username)

        return checkout_file

    '''
        Helper function for create_hda
    '''
    def create_new_hda_definition(self, element, asset_name, department, checkout_file, content_hda_filepath=None):
        # CREATE NEW HDA DEFINITION
        if content_hda_filepath is None:
            content_hda_filepath = checkout_file

        print("content hda filepath: ", content_hda_filepath)

        operator_name = str(element.get_parent() + "_" + element.get_department())
        operator_label = str((asset_name.replace("_", " ") + " " + element.get_department()).title())

        self.hda_definitions[department].copyToHDAFile(checkout_file, operator_name, operator_label)
        hda_type = hou.objNodeTypeCategory() if department in self.dcc_character_departments else hou.sopNodeTypeCategory()
        hou.hda.installFile(content_hda_filepath)
        print("hda type: ", hda_type)
        print("operator_name: ", operator_name)
        print("content_hda_filepath : ", content_hda_filepath)
        hda_definition = hou.hdaDefinition(hda_type, operator_name, content_hda_filepath)
        try:
            hda_definition.setPreferred(True)
        except:
            print("hda definition was not created")

    '''
        Helper function for create_hda
    '''
    def get_inside_node(self, type, department, node):
        # If it's a character and it's not a hair or cloth asset, we need to reach one level deeper.
        if type == AssetType.CHARACTER and department not in self.dcc_character_departments:
            inside = node.node("inside/geo/inside")
        else:
            inside = node.node("inside")

        return inside

    '''
        Helper function for create_hda
    '''
    def assemble_hda_instance(self, asset_name, department, inside):
        # Tab an instance of this new HDA into the asset you are working on
        try:
            hda_instance = inside.createNode(asset_name + "_" + department)
            print('created hda instance for ' + asset_name + ' in ' + department)
        except Exception as e:
            qd.error("HDA Creation Error. " + asset_name + "_" + department + " must not exist.")

        hda_instance.setName(department)
        self.tab_into_correct_place(inside, hda_instance, department)
        hda_instance.allowEditingOfContents()
        hda_instance.setSelected(True, clear_all_selected=True)

        return hda_instance

    '''
        Updates a content node.
    '''
    def update_content_node(self, parent, inside, asset_name, department, mode=UpdateModes.SMART, inherit_parameters=False, ignore_folders=["Asset Controls"]):

        # See if there's a content node with this department name already tabbed in.
        content_node = inside.node(department)

        # If the content node exists.
        if content_node is not None:
            # Delete it if we're in clean mode
            if mode == UpdateModes.CLEAN:
                content_node.destroy()
                content_node = None

        # Check if there's a published asset with this name
        try:
            is_published = self.published_definition(asset_name, department)
        except:
            is_published = False

        # If there isn't a published asset, delete the impostor!
        if not is_published and content_node:
            content_node.destroy()

        # This line checks to see if there's a published HDA with that name.
        elif is_published and not content_node:
            # Only create it if it's in the pipe.
            try:
                content_node = inside.createNode(asset_name + "_" + department)
            except:
                content_node = None

            # Check if node was successfully created
            if content_node:
                print("tabbing into correct place - inside, department: ", inside, department)
                self.tab_into_correct_place(inside, content_node, department)
                content_node.setName(department)
                # Some nodes will promote their parameters to the top level
                if inherit_parameters:
                    self.inherit_parameters_from_node(parent, content_node, mode, ignore_folders)


        return content_node

    '''
        Destroys unwanted content nodes if they remain in a network
    '''
    def destroy_if_there(self, inside, department):
        node = inside.node(department)
        if node is not None:
            node.destroy()
        node = None

    '''
        Check if a definition is the published definition or not
    '''
    def published_definition(self, asset_name, department):
        # Set the node type correctly
        category = hou.objNodeTypeCategory() if department in self.dcc_character_departments else hou.sopNodeTypeCategory()
        hou.hda.reloadAllFiles()

        # Get the HDA File Path
        hda_name = asset_name + "_" + department
        hda_file = hda_name + "_main.hdanc"
        new_hda_path = os.path.join(Project().get_project_dir(), "production", "hda", hda_file)
        old_hda_path = os.path.join(Project().get_project_dir(), "production", "otls", hda_file)

        hda_path = ""
        # Does it exist?
        if os.path.islink(new_hda_path):
            hda_path = os.readlink(new_hda_path)
        elif os.path.islink(old_hda_path):
            hda_path = os.readlink(old_hda_path)
        else:
            return False

        # If it does, grab the definition
        hou.hda.installFile(hda_path)
        hda_definition = hou.hdaDefinition(category, hda_name, hda_path)

        # If the definition failed for some reason, don't tab it in.
        if hda_definition is not None:
            hda_definition.setPreferred(True)
            return True
        else:
            return False

    '''
        Promote parameters from an inner node up to an outer node.
    '''
    def inherit_parameters_from_node(self, upper_node, inner_node, mode=UpdateModes.SMART, ignore_folders=[]):

        # Get the lists of parms
        upper_spare_parms = inner_node.spareParms()
        inner_parms = inner_node.parms()
        inner_parm_names = [parm.name() for parm in inner_parms]

        # Only remove the spare parms that are no longer on the inner_node
        if mode == UpdateModes.SMART:
            for upper_spare_parm in upper_spare_parms:
                if upper_parm.name() not in inner_parm_names:
                    upper_node.removeSpareParmTuple(inner_parm.parmTemplate())

        # Clean all spare parms
        elif mode == UpdateModes.CLEAN:
            upper_node.removeSpareParms()

        # Else, don't do anything
        elif mode == UpdateModes.FROZEN:
            return

        for inner_parm in inner_parms:

            # This isn't very elegant, but I need to check if any containing folders contain any substrings from ignore_folders
            in_containing_folder = False
            for folder in ignore_folders:
                for containingFolder in inner_parm.containingFolders():
                    if folder in containingFolder:
                        in_containing_folder = True
                        break
                if in_containing_folder:
                    break
            if in_containing_folder:
                continue
            # That's the end of the non-elegant solution

            # If not in the ignored folders, then either set the value or promote it
            upper_parm = upper_node.parm(inner_parm.name())
            if upper_parm is not None:
                upper_parm.set(inner_parm.eval())
            else:
                upper_node.addSpareParmTuple(inner_parm.parmTemplate(), inner_parm.containingFolders(), True)

    '''
        Helper function for create_hda()
    '''
    def tab_into_correct_place(self, inside, node, department):

        # If the node belongs inside a DCC Character, do the following
        if department in self.dcc_character_departments:

            # Hair and Cloth assets should be connected to geo. If it doesn't exist, throw an error.
            geo = inside.node("geo")
            if geo is None:
                qd.error("There should be a geo network. Something went wrong.")
                return

            # Attach the Hair or Cloth asset to the geo network.
            node.setInput(0, geo)

        # If the node belongs inside a DCC Geo, do the following
        else:

            # Shot_modeling and geo are our way of knowing where to insert nodes. If either of them is null, throw an error.
            geo = inside.node("geo")
            shot_modeling = inside.node("shot_modeling")
            if shot_modeling is None or geo is None:
                qd.error("There should be a shot_modeling and geo network. Something went wrong.")
                return None

            # If we're inserting a modify node, do the following
            if department == Department.MODIFY:

                # If there is a material node, put the modify node in between material and geo.
                material = inside.node("material")
                if material is not None:
                    node.setInput(0, geo)
                    material.setInput(0, node)

                # Else, stick it between geo and shot_modeling.
                else:
                    node.setInput(0, geo)
                    shot_modeling.setInput(0, node)

            # If we're inserting a material node, do the following
            elif department == Department.MATERIAL:

                # If there is a modify node, put the material node in between modify and shot_modeling.
                modify = inside.node("modify")
                if modify is not None:
                    node.setInput(0, modify)
                    shot_modeling.setInput(0, node)

                # Else, stick it between geo and shot_modeling.
                else:
                    node.setInput(0, geo)
                    shot_modeling.setInput(0, node)


        inside.layoutChildren()
        return node

    def rebuildAllAssets(self):
        # Recursively go through each node, and push the build button if exists.

        # Initialize stack.
        stack = []

        # Start at root.
        stack.append(hou.node("/obj"))

        # While stack is not empty,
        while len(stack) > 0:
            # Pop off the latest entry
            parent = stack.pop()

            # Re-grab children each generation (so that the results of the previous "build" apply
            for child in parent.children():

                # Add to stack
                stack.append(child)

                # Check if it is a dynamic content subnet, and press the build button. Else, continue.
                type_name = child.type().name()
                if "dcc_geo" in type_name or "dcc_character" in type_name or "dcc_set" in type_name:
                    build_button = child.parm("build")
                    if build_button:
                        build_button.pressButton()

    def commit_conversions(self):

        # Find all boxes that have nodes that were made by the conversion script
        boxes = []
        for item in hou.selectedItems():
            if not isinstance(item, hou.NetworkBox):
                continue

            # If the box doesn't have two nodes in it, it's definitely not ours
            nodes = item.nodes()
            if len(nodes) != 2:
                continue

            # If neither is named _new and/or neither is named _old, it's not one of ours
            if not "_new" in nodes[0].name() and not "_new" in nodes[1].name():
                continue
            if not "_old" in nodes[0].name() and not "_old" in nodes[1].name():
                continue

            # If the assets are not named the same, it's not one of ours
            print nodes[0].name()[:-4]
            print nodes[1].name()[:-4]

            if nodes[0].name()[:-4] != nodes[1].name()[:-4]:
                continue

            # If it passed the tests, add it to the list of network boxes we can work with
            boxes.append(item)

        print boxes

        # Don't go on unless there's a valid network box
        if len(boxes) < 1:
            qd.error("There aren't any network boxes created by the conversion script.")
            return

        for box in boxes:
            old_node = next((node for node in box.nodes() if "_old" in node.name()), None)
            new_node = next((node for node in box.nodes() if "_new" in node.name()), None)

            old_hda = old_node.type().definition()
            old_hda.setIcon(Environment().get_project_dir() + '/pipe/tools/_resources/1.png')

            publish.non_gui_publish_go(old_node, "Converted to V2")
            for child in new_node.allSubChildren():
                if "_material" in child.type().name() or "_modify" in child.type().name():
                    publish.non_gui_publish_go(child, "Converted from V1")

            # commit old_node
            # commit new_node
    '''this function has the set look for shot specific information, specifically if it has any animated objects'''
    def shotInfo(self, shot_name):
        print shot_name
        shot_file = os.path.join(Project().get_shots_dir(),shot_name, "anim", "main", "cache", "animated_props.json")

        shot_data=None
        try:
            with open(shot_file) as f:
                shot_data = json.load(f)
        except Exception as error:
            qd.error("No valid JSON file for " + shot_name)
            return

        for asset in shot_data:
            try:
                node=hou.node('./inside/'+asset['asset_name'])
                node.parm('space').set('2')
                node.parm('shot').set(shot_name)
            except:
                print 'error ', asset['asset_name']
