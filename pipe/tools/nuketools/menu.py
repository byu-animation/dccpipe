# import sip
import nuke
from importers import importer
from cloners import cloner
from publishers import publisher
from nukeutils import reload_scripts
from nukeutils import template_creator
from nukeutils import auto_compositor

menubar = nuke.menu("Nuke")
toolbar = nuke.toolbar("Nodes")

importer = importer.NukeImporter()
cloner = cloner.NukeCloner()
publisher = publisher.NukePublisher()
template_creator = template_creator.TemplateCreator()
auto_compositor = auto_compositor.AutoCompositor()

m = toolbar.addMenu("DCC Pipe Menu", icon="dcc.png")
m.addCommand("Clone", 'cloner.clone()', icon="clone.png")
m.addCommand("Publish", 'publisher.publish(quick=False)', icon="publish.png")
m.addCommand("Quick Publish", 'publisher.publish()', icon="quick_publish.png")
m.addCommand("Import template", 'importer.import_template()', icon="import.png")
m.addCommand("Create template from nodes", 'template_creator.create_from_current()', icon="assemble.svg")
m.addCommand("Auto composite", 'auto_compositor.auto_comp()', icon="auto-comp.svg")

# m.addCommand("Rollback", 'rollback.go()', icon="rollback.svg")
# m.addCommand("Reload Scripts", 'reload_scripts.go()', icon="reload.png")
