import sys
import os
# import pipelion.lion_mng.reader as Reader

class PipelionResources():

    @staticmethod
    def appName():
        return "Pipelion"

    @staticmethod
    def showTitle():
        return Reader.CurrentProduction().name

    @staticmethod
    def logo():
        return Reader.CurrentProduction().logo

    @staticmethod
    def logoSize():
        return 85

    @staticmethod
    def bodyTypes():
        return Reader.CurrentProduction().bodyTypes

    @staticmethod
    def departments(type=("","")):
        if type == ("",""):
            return Reader.CurrentProduction().departments
        else:
            return [x for x in Reader.CurrentProduction().departments if x.type == type[0]]

    @staticmethod
    def programs():
        return Reader.CurrentProduction().programs

    @staticmethod
    def isAdmin():
        return True

class Strings():
    remove = "Remove"
    dashboard = "Dashboard"
    settings = "Settings"
    admin_tools = "Admin Tools"
    shortcuts = "Shortcuts"
    checkedoutitems = "Checked Out Items"
    open = "Open In..."
    sync = "Sync"
    nochanges = "No Changes"
    delete = "Delete"
    rename = "Rename"
    checkout = "Checkout"
    change_dot_dot_dot = "Change..."
    broken_data = "Broken Data"
    items = "Items"
    path = "Path"
    type = "Type"
    departments = "Departments"
    size = "Size"

class Styles():
    openButton = '''
        background-color: yellow
    '''

    syncButton = '''
        background-color: green
    '''

    deleteButton = '''
        background-color: red
    '''

    renameButton = '''
        background-color: purple;
        color: white
    '''
    createButton = '''
        background-color: skyblue;

    '''

    changeButton = '''
        background-color: orange
    '''

    disabledButton = '''
        background-color: gray
    '''

    checkoutButton = '''
        background-color: green;
    '''
    tableBar = '''
        QLabel{background-color: #6a827c; font-size: 16px; color: white}
    '''
