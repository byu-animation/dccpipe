from pipe.tools.maya import *
from pipe.tools.maya.cloners import cloner
from pipe.tools.general import publisher

class ReloadScripts:

    def go(self):
    	reload(utils.reload_scripts)
    	reload(cloners.cloner)
    	# reload(exporters.exporter)
    	# reload(exporters.tagger)
    	# reload(importers.referencer)
    	# reload(publishers.publisher)
    	# reload(submitters)  # FIXME: causing problems.

        reload(publisher)
