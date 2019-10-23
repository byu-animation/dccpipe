# import sip
import nuke
# import checkout
# import publish
# import rollback
# import inspire
# import reload_scripts
# import nukeAutoComp
# import comp_template

menubar = nuke.menu("Nuke")
# Custom Lab Tools
toolbar = nuke.toolbar("Nodes")
m = toolbar.addMenu("DCC Pipe Menu", icon="dcc.png")
m.addCommand("Checkout", 'checkout.go()', icon="clone.png")
m.addCommand("Publish", 'publish.go()', icon="publish.png")
m.addCommand("Rollback", 'rollback.go()', icon="rollback.svg")
# m.addCommand("Auto Comp", 'nukeAutoComp.go()', icon="auto-comp.svg")
m.addCommand("Reload Scripts", 'reload_scripts.go()', icon="reload.png")
# m.addCommand("Grendel Template Comp", 'comp_template.go()', icon='auto-comp.svg')
