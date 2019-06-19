'''
    This is the plug-in pattern. We load modules as needed, and run
    the methods specified.
'''
import os
import sys
import json
import importlib
import tools
import traceback

class ToolError(Exception):
    def __init__(self, *args):
        message = ""
        for arg in args:
            message += str(arg)
        super(ToolError, self).__init__(message)

class NeedsUserInputError(ToolError):
    def __init__(self, *args):
        super(NeedsUserInputError, self).__init__(*args)

class MalformedToolFileError(ToolError):
    def __init__(self, *args):
        super(MalformedToolFileError, self).__init__(*args)

class NotSufficientFieldsError(ToolError):
    def __init__(self, *args):
        super(NotSufficientFieldsError, self).__init__(*args)

class Tool:

    pre = "pipe.tools."
    def __init__(self, tool_path, gui=False):
        # Load the tool as an object
        pwd = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
        tool_path = os.path.join(pwd, *tool_path.split(".")) + ".json"
        with open(tool_path) as f:
            tool_json = json.load(f)

        # Update this object's fields with the loaded json dict
        self.__dict__.update(tool_json)
        self.gui = gui

        # Create a QApplication
        if self.gui:
            try:
                from PySide import QtGui as QtWidgets
            except ImportError:
                from PySide2 import QtWidgets
            try:
                self.application = QtWidgets.QApplication(sys.argv)
            except:
                print "QApplication already loaded, using pre-existing"

        # Keep track of all modules that are loaded so we can check them fast
        self.loaded_modules = {}
        for method in self.methods:
            module_name = self.pre + method["module"]
            self.loaded_modules[module_name] = module_name in sys.modules

        print "Loaded {0}".format(self.name)

    def run(self, **kwargs):
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
        print "calling {0}\n".format(method["name"])
        method_call = getattr(sys.modules[self.pre + method["module"]], method["name"])

        args = ()
        if "needs" in method:
            for needed in method["needs"]:
                args += (self.__dict__[needed],)

        kwargs = {}
        if "optional" in method:
            for option in method["optional"]:
                if option is not None:
                    kwargs[option] = self.__dict__[option]

        # A variable that indicates the user wishes to cancel
        self.cancelled = False

        if "prompt" in method and method["prompt"]:
            method_call(self, *args, **kwargs)
        else:
            results = method_call(*args, **kwargs)

            if "provides" in method:
                for i, provided in enumerate(method["provides"]):
                    self.__dict__.update({provided, results[i]})

            if "conditional" in method:
                for i, condition in enumerate(method["conditional"]):
                    self.__dict__.update({provided, results[i]})

    def finished(self, **kwargs):
        self.__dict__.update(kwargs)

    # Check if this method can be skipped
    def must_run(self, method):

        # If everything is provided, this method does not need to run
        if "provides" in method:
            if not isinstance(method["provides"], list):
                raise MalformedToolFileError(method, "\"provides\" is not a list")

            for provided in method["provides"]:
                if not isinstance(provided, (str, unicode)):
                    raise MalformedToolFileError(
                            method,
                            "provided field is type {}, should be string".format(
                                type(provided)
                                )
                            )
                if not provided in self.__dict__ or not self.__dict__[provided]:
                    return True

            return False

        else:
            return True

    # This verifies that the tool can run at all by checking needed fields
    # and checking needed modules (it tries to load them if they aren't already)
    # It is likely this will fail if a gui method is run in a non-gui environment,
    # but will be caught in the run loop in self.run().
    def can_run(self, method):

        # If we are in non-gui mode and require this method (which is a prompt),
        # then we must error.
        if "prompt" in method and method["prompt"] and not self.gui:
            raise NeedsUserInputError(
                "User input is needed through the following GUI method: ",
                self.pre + method["module"] + "." + method["name"] + "()"
                )

        # The method might require certain fields
        if "needs" in method:
            if not isinstance(method["needs"], list):
                raise MalformedToolFileError(method["name"], ": \"needs\" is not a list")

            for needed in method["needs"]:
                if not needed in self.__dict__ or self.__dict__[needed] is None:
                    raise NotSufficientFieldsError(method["name"], ": needs ", needed)

        # If the module is not loaded, try loading it
        # This is likely to throw an exception, which will be caught in the for loop of self.run()
        if not self.loaded_modules[self.pre + method["module"]]:
            importlib.import_module(self.pre + method["module"])

        return True

    # gui and non-gui safe ways of displaying errors
    def display_error(self, message, details):
        if self.gui:
            import pipe.gui.quick_dialogs as quick_dialogs
            quick_dialogs.error(message, details)
        else:
            print "{0}\n{1}".format(message, details)
