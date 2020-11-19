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

        stage = hou.node("/stage/TestNet")
        obj = hou.node("/obj")

        #CODE TO DELETE EVERYTHING FOR TESTING PURPOSES
        for node in stage.children():
            node.destroy()


        objObjects = obj.children()
        characters = []
        props = []
        sets = {}

        for child in objObjects:

            print("Child: " + str(child))
            print(child.type())

            if child.type().name() == "dcc_character":
                name = str(child)
                character = stage.createNode("sopimport", name)

                hou.cd(child.path())
                sopGeo = hou.node("inside/geo")
                path = sopGeo.path()
                character.parm("soppath").set(path)

                material = stage.createNode("materiallibrary", name + "_Materials")
                material.setInput(0, character)

                characters.append(material)

            if child.type().name() == "dcc_geo":
                name = str(child)
                geo = stage.createNode("sopimport", name)

                hou.cd(child.path())
                sopGeo = hou.node("inside/OUT")
                path = sopGeo.path()
                geo.parm("soppath").set(path)

                material = stage.createNode("materiallibrary", name + "_Materials")
                material.setInput(0, geo)

                props.append(material)


            if child.type().name() == "dcc_set":
                setName = str(child)
                setChildren = child.children()[0].children()
                set = []
                for setGeo in setChildren:
                    name = setName + "_" + str(setGeo)
                    setGeoNode = stage.createNode("sopimport", name)

                    hou.cd(setGeo.path())
                    sopGeo = hou.node("inside/OUT")
                    path = sopGeo.path()
                    setGeoNode.parm("soppath").set(path)

                    material = stage.createNode("materiallibrary", name + "_Materials")
                    material.setInput(0, setGeoNode)

                    set.append(material)

                sets[setName] = set

            print("")
        mergeNode = stage.createNode("merge", "MERGE_ALL")
        mergeNodes = []

        characterMerge = stage.createNode("merge", "Character_Merge")
        mergeNodes.append(characterMerge)
        i = 0
        for node in characters:
            characterMerge.setInput(i, node)
            i+=1

        propMerge = stage.createNode("merge", "Prop_Merge")
        mergeNodes.append(propMerge)
        i = 0
        for node in props:
            propMerge.setInput(i, node)
            i+=1

        setMergeAll = stage.createNode("merge", "Set_Merge_ALL")
        setMergeNodes = []
        mergeNodes.append(setMergeAll)
        print("sets: " + str(sets))
        for set in sets:
            print(set)
            name = "Set_Merge_" + str(set)
            setMerge = stage.createNode("merge", name)
            setMergeNodes.append(setMerge)
            i = 0
            for node in sets[set]:
                setMerge.setInput(i, node)
                i+=1

        i = 0
        for node in setMergeNodes:
            setMergeAll.setInput(i, node)
            i+=1

        i = 0
        for node in mergeNodes:
            mergeNode.setInput(i, node)
            i+=1

        print("\n")
