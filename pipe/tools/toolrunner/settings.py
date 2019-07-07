import sys
import os.path as path
import json

class ToolRunnerSettingNotFoundError(Exception):
    '''
    Raised when there is not a setting associated with a given key
    '''
    pass

class ToolRunnerSettings:
    def __init__(self, directory):
        self.directory = directory

        self.settings = {}
        with open(path.join(self.directory, "settings.json"), "r") as f:
            self.settings = json.load(f)

        self.preferences = {}
        try:
            with open(path.join(self.directory, "preferences.json"), "r") as f:
                self.preferences = json.load(f)
        except:
            print("No user preferences found.")

    def get_pystylesheet(self):
        return self.get("PYSTYLESHEET")

    def get(self, key):
        '''
        User settings override application defaults.
        '''
        if key in self.preferences and key in self.settings:
            return self.preferences[key]

        elif key in self.settings:
            return self.settings[key]

        else:
            raise ToolRunnerSettingNotFoundError()
