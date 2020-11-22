import sys, os, json
import shutil
import json

import hou

from pipe.gui import quick_dialogs
from pipe.gui.select_from_list import SelectFromList
from pipe.am.project import Project
from pipe.am.body import AssetType
from pipe.am.environment import Environment, Department  # , Status

from PySide2 import QtCore
from PySide2 import QtWidgets
from PySide2.QtCore import Signal, Slot


'''
USD Stager is a class dedicated to scripts that convert /obj objects into /stage
objects so that the artists don't have to do that manually. Specifically,
this will deal with importing SOPs from DCC nodes, and then re-attaching the
materials to them automatically.
'''
class USD_Stager:

    def __init__(self):
        self.select_from_list_dialog = None

    def initializeStageNetwork(self):
        #WIP version, currently testing in Houdini's python editor
        #import hou

        stage = hou.node("/stage")
        obj = hou.node("/obj")

        #CODE TO DELETE EVERYTHING FOR TESTING PURPOSES
        #for node in stage.children():
        #    node.destroy()


        objObjects = obj.children()
        characters = []
        props = []
        sets = {}

        for child in objObjects:

            #print("Child: " + str(child))
            #print(child.type())

            if child.type().name() == "dcc_character":
                print("Working on " + str(child))
                name = str(child)
                character = stage.createNode("sopimport", name)

                pathToSop = setSopPath(child, character, True)
                materialPaths = getMaterials(pathToSop)

                material = stage.createNode("materiallibrary", name + "_Materials")
                material.setInput(0, character)
                setMaterialPath(child, material, True)

                fillMaterials(material, materialPaths)

                characters.append(material)

            if child.type().name() == "dcc_geo":
                print("Working on " + str(child))
                name = str(child)
                geo = stage.createNode("sopimport", name)

                pathToSop = setSopPath(child, geo)
                materialPaths = getMaterials(pathToSop)

                material = stage.createNode("materiallibrary", name + "_Materials")
                material.setInput(0, geo)
                setMaterialPath(child, material)

                fillMaterials(material, materialPaths)

                props.append(material)


            if child.type().name() == "dcc_set":
                print("Working on " + str(child))
                setName = str(child)
                setChildren = child.children()[0].children()
                set = []
                for setGeo in setChildren:
                    print("\tWorking on " + str(setGeo))
                    name = setName + "_" + str(setGeo)
                    setGeoNode = stage.createNode("sopimport", name)

                    pathToSop = setSopPath(setGeo, setGeoNode)
                    materialPaths = getMaterials(pathToSop)

                    material = stage.createNode("materiallibrary", name + "_Materials")
                    material.setInput(0, setGeoNode)
                    setMaterialPath(setGeo, material)

                    fillMaterials(material, materialPaths)

                    set.append(material)

                sets[setName] = set

            #print("")
        mergeNode = stage.createNode("merge", "MERGE_ALL")
        mergeNodes = []

        characterMerge = stage.createNode("merge", "Character_Merge")
        mergeNodes.append(characterMerge)
        connectNodes(characters, characterMerge)

        propMerge = stage.createNode("merge", "Prop_Merge")
        mergeNodes.append(propMerge)
        connectNodes(props, propMerge)

        setMergeAll = stage.createNode("merge", "Set_Merge_ALL")
        setMergeNodes = []
        mergeNodes.append(setMergeAll)
        #print("sets: " + str(sets))
        for set in sets:
            #print(set)
            name = "Set_Merge_" + str(set)
            setMerge = stage.createNode("merge", name)
            setMergeNodes.append(setMerge)
            connectNodes(sets[set], setMerge)

        connectNodes(setMergeNodes, setMergeAll)
        connectNodes(mergeNodes, mergeNode)

        mergeNode.setDisplayFlag(True)
        stage.layoutChildren(items=(stage.children()))


        print("\n")

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
