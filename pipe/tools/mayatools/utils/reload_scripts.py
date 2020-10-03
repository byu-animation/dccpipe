from pipe.tools.mayatools import *
from pipe.tools.mayatools.cloners import cloner as maya_cloner
from pipe.tools.mayatools.creators import creator as maya_creator
from pipe.tools.mayatools.publishers import publisher as maya_publisher
from pipe.tools.mayatools.utils import utils as maya_utils
from pipe.tools.mayatools.utils import education as edu
from pipe.tools.mayatools.exporters import alembic_exporter as alembic_exporter
from pipe.tools.mayatools.exporters import fbx_exporter as fbx_exporter
from pipe.tools.mayatools.exporters import exporter as exporter
from pipe.tools.mayatools.exporters import json_exporter as json_exporter
from pipe.tools.mayatools.importers import referencer as maya_referencer
from pipe.tools.mayatools.importers import reference_importer as reference_importer
from pipe.tools.mayatools.exporters import tagger as maya_tagger
from pipe.tools.mayatools.submitters import playblaster as maya_playblaster

from pipe.gui import select_from_list as sfl


class ReloadScripts:

    def go(self):
        reload(utils.reload_scripts)
        reload(maya_creator)
        reload(maya_cloner)
        reload(maya_publisher)
        reload(maya_utils)
        reload(edu)
        reload(alembic_exporter)
        reload(fbx_exporter)
        reload(exporter)
        reload(json_exporter)
        reload(maya_referencer)
        reload(reference_importer)
        reload(maya_tagger)
        reload(maya_playblaster)
        reload(sfl)
