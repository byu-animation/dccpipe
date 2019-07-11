import os

# Other export scripts
import pipe.tools.mayatools.utils.utils as maya_utils
from pipe.tools.mayatools.exporters.alembic_exporter import AlembicExporter
from pipe.tools.mayatools.exporters.json_exporter import JSONExporter
from pipe.tools.mayatools.prompts import Prompts

# We're going to need asset management module
from pipe.am import Environment, Project

# Minimal UI
from pipe.gui.checkbox_options import CheckBoxOptions
from pipe.gui.select_from_list import SelectFromList

# Import Tools
from pipe.tools.general.publisher import Publisher

try:
    from PySide.QtCore import Slot
except ImportError:
    from PySide2.QtCore import Slot


'''
    Works as a publisher, but adds an additional scene prep dialog at the beginning,
    and runs the Maya export scripts at the end.
'''
class MayaPublisher:

    def __init__(self, gui=True, src=None):
        super(MayaPublisher, self).__init__(gui, src)

    def publish(self):
        pass

        def maya_main_window():
	'''Return Maya's main window'''
	for obj in QtWidgets.qApp.topLevelWidgets():
		if obj.objectName() == 'MayaWindow':
			return obj
	raise RuntimeError('Could not find MayaWindow instance')

#TODO: FIXME. LOTS OF STUFF TO DO PRIOR TO PUBLISHING FROM MAYA. ALL THE FOLLOWING.
def clear_construction_history():
	pm.delete(constructionHistory=True, all=True)

def freeze_transformations():
	objects = pm.ls(transforms=True)
	for sceneObj in objects:
	    pm.makeIdentity(sceneObj, apply=True)


def post_publish():
	element = maya_publish_dialog.result

	if maya_publish_dialog.published:
		if not cmds.file(q=True, sceneName=True) == '':
			cmds.file(save=True, force=True) #save file

		#Publish
		user = maya_publish_dialog.user
		src = maya_publish_dialog.src
		comment = maya_publish_dialog.comment
		publishElement(element, user, src, comment)

def publishElement(element, user, src, comment):
	dst = element.publish(user, src, comment)
	#Ensure file has correct permissions
	try:
		os.chmod(dst, 0660)
	except:
		pass

	#freeze transformations and clear history
	if maya_publish_dialog.clearHistoryCheckbox.isChecked():
		clear_construction_history()
		try:
			freeze_transformations()
		except:
			freeze_error_msg = ("Failed to freeze transformations, probably because "
			"there are one or more keyframed values in your object. Remove all "
			"keyframed values and expressions from your object and try again.")
			cmds.confirmDialog(title="Freeze Transformations Error", message=freeze_error_msg)
			print(freeze_error_msg)

	#Export a playblast
	print 'TODO: export playblast'
	print element.get_name()

	#Export Alembics
	print 'Publish Complete. Begin Exporting Alembic, or JSON if set'
	body = Project().get_body(element.get_parent())
	try:
		alembic_exporter.go(element=element)
	except:
		print("alembic export failed.")
	if body and body.is_asset():
		json_exporter.go(body, body.get_type())
	else:
		json_exporter.go(body, type="shot")
	noEducationalLicence()
	#sketchfab_exporter.go(element=element, dept=maya_publish_dialog.department)

def noEducationalLicence():
	pm.FileInfo()['license'] = 'education'
	fileName = pm.sceneName()
	pm.saveFile()
	message_gui.info('This Maya file has been converted to an education licence')


def go():
	parent = maya_main_window()
	filePath = cmds.file(q=True, sceneName=True)
	if not filePath:
		filePath = Environment().get_user_workspace()
		filePath = os.path.join(filePath, 'untitled.mb')
		filePath = pipeline_io.version_file(filePath)
		cmds.file(rename=filePath)
		cmds.file(save=True)
	global maya_publish_dialog
	maya_publish_dialog = PublishWindow(filePath, parent, [Department.MODEL, Department.RIG, Department.LAYOUT, Department.ANIM, Department.CFX, Department.CYCLES])
	maya_publish_dialog.finished.connect(post_publish)

def non_gui_publish(element, user, src, comment):
	dst = element.publish(user, src, comment)
	#Ensure file has correct permissions
	try:
		os.chmod(dst, 0660)
	except:
		pass
	print 'TODO: export playblast'
    print element.get_name()


        #
        #
        #     if created:
        #         project = Project()
        #         body = project.create_asset(name, asset_type=type)
        #         if body == None:
        #             # print a message about failure/duplicate
        #             qd.error("Body not found, publish failed.")
        #         else:
        #             # correct so far
        #             # TODO: publish
        #             prepare_scene_file()
        #             # show the gui, get the element. To list elements, get the body and get the department
        #             department = "model"  # hard-coding model for now since this is Maya
        #             asset_list = body.list_elements(department)
        #             self.item_gui = sfl.SelectFromList(l=asset_list, parent=maya_main_window(), title="Select an asset to publish to")
        #             self.item_gui.submitted.connect(self.results)
        #     else:
        #         qd.error("Asset creation failed.")
        #
        # def results(self, value):
        #     print("Final value: ", value[0])
        #     filename = value[0]
        #
        #     project = Project()
        #     body = project.get_body(filename)
        #
        #     # get the element for the model dept and the user, and using that publish
        #     selected_element = body.get_element("model")
        #
        #     user = Environment().get_user()
        #     post_publish(selected_element, user, published=True, comment="No comment.")
        #
        #     qd.info("Asset created successfully (but not really, yet).", "Success")
