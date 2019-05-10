'''
name
  The name of the tool.

fields
  The fields that will be passed between methods of this tool.

methods
  The order in which methods on the tool will be called.

  module (list)
    If this method must be run and cannot be skipped, and this module is
    not available, error.

  provides (list)
    The method will provide these outputs, and if they are already provided,
    the method will be skipped.

  needs (list)
    The method will require these inputs, and fail if they do not exist.

  conditional (list)
    The method will provide these outputs conditionally. They are NOT considered
    when deciding whether or not to run the method.

  optional (list)
    The method can take in these inputs, but does not need them.
'''
import os
import sys
import json
import importlib
import tools

class tool:
    def __init__(self, path, non_gui=False):
        # Load the tool as an object
        pwd = os.path.dirname(os.path.realpath(__file__))
        tool_path = path.split(".")
        tool = json.load(tool_path)

        # Update this object's fields with the loaded json dict
        self.__dict__.update(tool)
        self.non_gui = non_gui

        # Load gui package if this is non-gui
        if not self.non_gui:
            import pipe.gui.quick_dialogs as quick_dialogs

        # Keep track of all modules that are loaded so we can check them fast
        self.loaded_modules = {}
        for method in self.methods:
            module_name = "tools." + method["module"]
            self.loaded_modules[module_name] = module_name in sys.__modules__

    def run(self, kwargs):
        try:
            # Update this object with the new arguments
            self.__dict__.update(kwargs)

            # Run all methods. If one fails, it will throw an exception
            for method in self.methods:
                if self.must_run(method):
                    self.can_run(method)
                    self.call(method)

        except Exception as e:
            # Display error and details
            message = "Error running {0}".format(self.name)
            details = "{0}\n".format(kwargs)
            details += str(e)
            self.display_error(message, details)

    # Load the module, call the method
    def call(self, method):
        method_call = getattr(sys.modules["tools." + method["module"]], method["name"])
        # we pass in self because sometimes PySide needs to store references on an object in memory
        # (as is the case with Maya)
        method_call(self)

    # Check if this method can be skipped
    def must_run(self, method):

        # If everything is provided, this method does not need to run
        if "provides" in method:
            if not isinstance(method["provides"], list):
                raise MalformedToolFileError(method, "\"provides\" is not a list")

            provides_all = True

            for provided in method["provides"]:
                if not instanceof(provided, str):
                    raise MalformedToolFileError(method, "provided field is type {}, should be string".format(type(provided)))

                if provided not in self.fields or self.fields[provided] is None:
                    provides_all = False

            return not provides_all

        else:
            return True

    def can_run(self, method):

        # The method might require certain fields
        if "needs" in method:
            if not isinstance(method["needs"], list):
                raise MalformedToolFileError(method, "\"needs\" is not a list")

            for needed in method["needs"]:
                if not needed in self.fields or self.fields[needed] is None:
                    raise NotSufficientFieldsError(method, needed)

        # If the module is not loaded, try loading it
        # This is likely to throw an exception, which will be caught in the for loop of self.run
        if not self.loaded_modules["tools." + method["module"]]:
            importlib.import_module("tools." + method["module"])

    # Gui and non-gui safe way of displaying errors
    def display_error(self, message, details):
        if self.non_gui:
            print "{0}\n{1}".format(message, details)
        else:
            quick_dialogs.error(message, details)
