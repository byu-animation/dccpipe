'''
    This is the plug-in pattern. We load modules as needed, and run
    the methods specified.
'''
import os
import sys
import json
import importlib
import tools
import jsonpickle
import traceback

class MalformedToolFileError(Exception):
    def __init__(self, *args):
        message = ""
        for arg in args:
            message += str(args)
        super(MalformedToolFileError, self).__init__(message)

class NotSufficientFieldsError(Exception):
    def __init__(self, *args):
        message = ""
        for arg in args:
            message += str(args)
        super(NotSufficientFieldsError, self).__init__(message)

class Tool:
    self.pre = "pipe.tools"
    def __init__(self, tool_path, non_gui=False):
        # Load the tool as an object
        pwd = os.path.dirname(os.path.realpath(__file__))
        tool_path = os.path.join(pwd, *tool_path.split(".")) + ".json"
        with open(tool_path) as f:
            tool_json = json.load(f)

        # Update this object's fields with the loaded json dict
        self.__dict__.update(tool_json)
        self.non_gui = non_gui

        # Load gui package if this is non-gui
        if not self.non_gui:
            import pipe.gui.quick_dialogs as quick_dialogs

        # Keep track of all modules that are loaded so we can check them fast
        self.loaded_modules = {}
        for method in self.methods:
            module_name = method["module"]
            self.loaded_modules[module_name] = module_name in sys.modules

    def run(self, kwargs={}):
        try:
            # Update this object with the new arguments
            self.__dict__.update(kwargs)

            # Run all methods. If one fails, it will throw an exception
            for method in self.methods:
                if self.must_run(method) and self.can_run(method):
                    self.call(method)
                    if self.cancelled:
                        break

        except Exception as e:
            # Display error and details
            message = "Error running {0}".format(self.name)
            details = "{0}\n".format(kwargs)
            details += str(e) + "\n"
            details += str(traceback.format_exc())
            self.display_error(message, details)

    # Load the module, call the method
    def call(self, method):
        method_call = getattr(sys.modules[method["module"]], method["name"])

        args = ()
        if "needs" in method:
            for needed in method["needs"]:
                args += self.__dict__[needed]

        kwargs = {}
        if "optional" in method:
            for option in method["optional"]:
                if option is not None:
                    kwargs[option] = self.__dict__[option]

        # A variable that indicates the user wishes to cancel
        self.cancelled = False

        if "prompt" in method and method["prompt"]:
            method_call(self, finished, *args, **kwargs)
        else:
            results = method_call(*args, **kwargs)

            if "provides" in method:
                for i, provided in enumerate(method["provides"]):
                    self.__dict__.update({provided, results[i]})

            if "conditional" in method:
                for i, condition in enumerate(method["conditional"]):
                    self.__dict__.update({provided, results[i]})

        def finished(**kwargs):
            self.__dict__.update(kwargs)

    # Check if this method can be skipped
    def must_run(self, method):

        # If everything is provided, this method does not need to run
        if "provides" in method:
            if not isinstance(method["provides"], list):
                raise MalformedToolFileError(method, "\"provides\" is not a list")

            provides_all = True

            for provided in method["provides"]:
                if not isinstance(provided, (str, unicode)):
                    raise MalformedToolFileError(method, "provided field is type {}, should be string".format(type(provided)))

                if provided not in self.fields or self.fields[provided] is None:
                    provides_all = False

            return not provides_all

        else:
            return True

    # This verifies that the tool can run at all by checking needed fields
    # and checking needed modules (it tries to load them if they aren't already)
    # It is likely this will fail if a gui method is run in a non-gui environment,
    # but will be caught in the run loop in self.run().
    def can_run(self, method):

        # The method might require certain fields
        if "needs" in method:
            if not isinstance(method["needs"], list):
                raise MalformedToolFileError(method, "\"needs\" is not a list")

            for needed in method["needs"]:
                if not needed in self.fields or self.fields[needed] is None:
                    raise NotSufficientFieldsError(method, needed)

        # If the module is not loaded, try loading it
        # This is likely to throw an exception, which will be caught in the for loop of self.run()
        print method
        if not self.loaded_modules[method["module"]]:
            importlib.import_module(method["module"])

        return True

    # gui and non-gui safe ways of displaying errors
    def display_error(self, message, details):
        if self.non_gui:
            print "{0}\n{1}".format(message, details)
        else:
            quick_dialogs.error(message, details)
