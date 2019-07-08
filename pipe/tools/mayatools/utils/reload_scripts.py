from pipe.tools.mayatools import *
from pipe.tools.mayatools.cloners import cloner
from pipe.tools.mayatools.publishers import publisher as maya_publisher
from pipe.tools.general import prompts
from pipe.tools.general import gui_tool
from pipe.tools.general import publisher

class ReloadScripts:

    def go(self):
    	reload(utils.reload_scripts)
    	reload(cloners.cloner)
        reload(prompts)
        reload(gui_tool)
        reload(publisher)
        reload(maya_publisher)
    	# reload(exporters.exporter)
    	# reload(exporters.tagger)
    	# reload(importers.referencer)
    	# reload(publishers.publisher)
    	# reload(submitters)  # FIXME: causing problems.

        reload(publisher)
