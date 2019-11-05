from pipe.tools.nuketools import *
from pipe.tools.nuketools.importers import importer

def go():
    # reload(nukeutils.reload_scripts)
    reload(importer)
    print("reloaded")
