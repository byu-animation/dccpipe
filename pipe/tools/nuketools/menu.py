# import sip
import nuke
from importers import importer
from cloners import cloner
from publishers import publisher
from nukeutils import reload_scripts
# import checkout
# import publish
# import rollback
# import inspire
# import reload_scripts
# import nukeAutoComp
# import comp_template

menubar = nuke.menu("Nuke")
toolbar = nuke.toolbar("Nodes")

importer = importer.NukeImporter()
cloner = cloner.NukeCloner()
publisher = publisher.NukePublisher()

m = toolbar.addMenu("DCC Pipe Menu", icon="dcc.png")
m.addCommand("Clone", 'cloner.clone()', icon="clone.png")
m.addCommand("Publish", 'publisher.publish()', icon="quick_publish.png")
m.addCommand("Import template", 'importer.import_template()', icon="import.png")
# m.addCommand("Create template from nodes", 'publisher.publish()', icon="assemble.svg")
# m.addCommand("Auto Comp", 'nukeAutoComp.go()', icon="auto-comp.svg")

# m.addCommand("Rollback", 'rollback.go()', icon="rollback.svg")
# m.addCommand("Reload Scripts", 'reload_scripts.go()', icon="reload.png")
