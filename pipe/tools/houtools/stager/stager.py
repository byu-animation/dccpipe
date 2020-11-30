import sys, os, json
import shutil
import json

import hou

from pipe.gui import quick_dialogs
from pipe.gui.select_from_list import SelectFromList
from pipe.am.project import Project
from pipe.am.body import AssetType
from pipe.am.environment import Environment, Department  # , Status

import pipe.gui.quick_dialogs as qd

from PySide2 import QtCore
from PySide2 import QtWidgets
from PySide2.QtCore import Signal, Slot


'''
Stager is a class dedicated to scripts that convert /obj objects into /stage
objects so that the artists don't have to do that manually. Specifically,
this will deal with importing SOPs from DCC nodes, and then re-attaching the
materials to them automatically.
'''
class Stager:

    def __init__(self):
        self.select_from_list_dialog = None

    def initializeStageNetwork(self):
        stage = hou.node("/stage")
        obj = hou.node("/obj")
        objObjects = obj.children()
        mergeNode = self.iterateAndMergeObjects(objObjects)

        #import camera
        camera = stage.createNode("sceneimport", "camera_import")
        camera.parm("filter").set("!!OBJ/CAMERA!!")
        camera.parm("objects").set("*")
        camera.setInput(0, mergeNode)

        #create light merge
        lightMerge = stage.createNode("merge", "Light_Merge")
        lightMerge.setInput(0, camera)

        #create renderman node
        renderNode = stage.createNode("hdprman", "OUT_RENDER")
        renderNode.setInput(0, lightMerge)

        renderNode.setDisplayFlag(True)
        stage.layoutChildren(items=(stage.children()))

        print("\n")


    def importAssetToStage(self):
        stage = hou.node("/stage")
        obj = hou.node("/obj")
        selected = hou.selectedNodes()
        if len(selected) < 1:
            qd.error("No Nodes selected, select at least one DCC Node to import to stage. \nNote:Only DCC Nodes are supported!")
        else:
            mergeNode = self.iterateAndMergeObjects(selected)
            #mergeNode.setDisplayFlag(True)
            stage.layoutChildren(items=(stage.children()))
            qd.info("Asset Imported Successfully!")


    def iterateAndMergeObjects(self, objects):
        stage = hou.node("/stage")
        obj = hou.node("/obj")

        #CODE TO DELETE EVERYTHING FOR TESTING PURPOSES
        #for node in stage.children():
        #    node.destroy()


        #objObjects = obj.children()
        characters = []
        props = []
        sets = {}

        for child in objects:

            if child.type().name() == "dcc_character":
                material = self.createAndFillSop(stage, child, True)
                characters.append(material)

            if child.type().name() == "dcc_geo":
                material = self.createAndFillSop(stage, child, False)
                props.append(material)

            if child.type().name() == "dcc_set":
                print("Working on " + str(child))
                setName = str(child)
                setChildren = child.children()[0].children()
                set = []
                for setGeo in setChildren:
                    material = self.createAndFillSop(stage, setGeo, False)
                    set.append(material)

                sets[setName] = set

        #connect geo nodes together
        mergeNode = stage.createNode("merge", "MERGE_ALL_GEO")
        mergeNodes = []

        if len(characters) > 0:
            characterMerge = stage.createNode("merge", "Character_Merge")
            mergeNodes.append(characterMerge)
            self.connectNodes(characters, characterMerge)

        if len(props) > 0:
            propMerge = stage.createNode("merge", "Prop_Merge")
            mergeNodes.append(propMerge)
            self.connectNodes(props, propMerge)

        if len(sets) > 0:
            setMergeAll = stage.createNode("merge", "Set_Merge_ALL")
            setMergeNodes = []
            mergeNodes.append(setMergeAll)

            for set in sets:
                #print(set)
                name = "Set_Merge_" + str(set)
                setMerge = stage.createNode("merge", name)
                setMergeNodes.append(setMerge)
                self.connectNodes(sets[set], setMerge)

            self.connectNodes(setMergeNodes, setMergeAll)

        self.connectNodes(mergeNodes, mergeNode)

        return mergeNode




    def createAndFillSop(self, stage, child, isCharacter=False):
        print("Working on " + str(child))
        name = str(child)
        sopImport = stage.createNode("sopimport", name)

        pathToSop = self.setSopPath(child, sopImport, isCharacter)
        materialPaths = self.getMaterials(pathToSop)

        materialLibraryNode = stage.createNode("materiallibrary", name + "_Materials")
        materialLibraryNode.setInput(0, sopImport)
        self.setMaterialPath(child, materialLibraryNode, isCharacter)

        self.fillMaterials(materialLibraryNode, materialPaths)

        return materialLibraryNode


    def setSopPath(self, child, sopImportNode, isCharacter=False):

        pathString = "inside/OUT"

        if isCharacter:
            pathString = "inside/geo/inside/OUT"

        hou.cd(child.path())
        sopGeo = hou.node(pathString)
        path = sopGeo.path()

        result = sopImportNode.parm("soppath").set(path)

        return path

    def setMaterialPath(self, child, materialLibrary, isCharacter=False):

        pathString = "inside/material/material_network/material_network"

        if isCharacter:
            pathString = "inside/geo/inside/material/material_network/material_network"

        hou.cd(child.path())
        materialNetwork = hou.node(pathString)
        path = materialNetwork.path()

        materialLibrary.parm("matnet").set(path)
        materialLibrary.parm("fillmaterials").pressButton()

    def getMaterials(self, pathToSop):
        sop = hou.node(pathToSop)
        #pathAttrib = sop.geometry().findPrimAttrib("path")
        shopAttrib = sop.geometry().findPrimAttrib("shop_materialpath")

        materialPaths = {}

        #TODO: Find a more optimized way of getting materials?
        for prim in sop.geometry().prims():
            pathValue = prim.attribValue("path")
            pathValue = pathValue.replace(":", "_")
            pathValue = pathValue[0:pathValue.rfind('/')]

            if shopAttrib is not None:
                try:
                    shopValue = prim.attribValue("shop_materialpath")

                    if pathValue not in materialPaths and shopValue is not "":
                        materialPaths[pathValue] = shopValue
                except:
                    print(str(pathToSop) + " does not have any materials assigned")

        return materialPaths

    def fillMaterials(self, material, materialPaths):
        materialCount = material.parm("materials").evalAsInt()
        #print(materialCount)
        for i in range(1, materialCount+1):
            geoParm = "geopath" + str(i)
            matParm = "matnode" + str(i)
            materialVOP = material.parm(matParm).eval()
            pos = materialVOP.find('/obj')
            #print(pos.type())
            materialVOP = materialVOP[pos:]
            #print(materialVOP)

            #potential for multiple geo paths so we need to first find
            #and then concatenate the paths together
            combinedGeoPath = ""
            for key, value in materialPaths.items():
                if value == materialVOP:
                    combinedGeoPath+= key + " "

            try:
                material.parm(geoParm).set(combinedGeoPath)
            except:
                print("exception occurred")
                continue

    def connectNodes(self, upperNodes, lowerNode):
        i = 0
        for node in upperNodes:
            lowerNode.setInput(i, node)
            i+=1
