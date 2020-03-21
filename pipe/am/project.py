import os
import shutil

from am.body import Body, Asset, Shot, Tool, CrowdCycle, AssetType
from am.element import Checkout, Element
from am.environment import Department, Environment, User
from am import pipeline_io
from am.registry import Registry



class Project:
	'''
	Class describing a dcc project.
	'''

	def __init__(self):
		'''
		creates a Project instance for the currently defined project from the environment
		'''
		self._env = Environment()

	@staticmethod
	def default_departments():
		'''
		return a list of all departments
		'''
		return Department.ALL

	@staticmethod
	def houdini_default_departments():
		'''
		return a list of houdini-specific departments
		'''
		return Department.HOUDINI_DEPTS

	@staticmethod
	def prop_export_departments():
		'''
		return a list of departments that props are exported to
		'''
		return Department.PROP_EXPORT_DEPARTMENTS

	@staticmethod
	def char_export_departments():
		'''
		return a list of departments that chars are exported to
		'''
		return Department.ACTOR_EXPORT_DEPARTMENTS

	@staticmethod
	def set_export_departments():
		'''
		return a list of departments that sets are exported to
		'''
		return Department.SET_EXPORT_DEPARTMENTS

	@staticmethod
	def shot_export_departments():
		'''
		return a list of departments that shots are exported to
		'''
		return Department.SHOT_EXPORT_DEPARTMENTS

	def get_name(self):
		'''
		return the name of the this project
		'''
		return self._env.get_project_name()

	def get_project_dir(self):
		'''
		return the absolute filepath to the directory of this project
		'''
		return self._env.get_project_dir()

	def get_assets_dir(self):
		'''
		return the absolute filepath to the assets directory of this project
		'''
		return self._env.get_assets_dir()

	def get_shots_dir(self):
		'''
		return the absolute filepath to the shots directory of this project
		'''
		return self._env.get_assets_dir()

	def get_rendered_shots_dir(self):
		rendered_shots = Environment().get_shots_dir()

		return rendered_shots

	def get_tools_dir(self):
		'''
		return the absolute filepath to the tools directory of this project
		'''
		return self._env.get_tools_dir()

	def get_crowds_dir(self):
		'''
		return the absolute filepath to the crowds directory of this project
		'''
		return self._env.get_crowds_dir()

		#TODO create a get tabs dir in the byuam environment module
	def get_tabs_dir(self):
		'''
		return the absolute filepath to the xml tabs directory of this project
		'''
		return os.path.join(self._env.get_project_dir(),'production/tabs')

	def get_users_dir(self):
		'''
		return the absolute filepath to the users directory of this project
		'''
		return self._env.get_users_dir()

	def get_submission_location(self):
		return pipeline_io.get_settings_info(self.get_project_dir(), "submission_location")

	def set_submission_location(self, location):
		return pipeline_io.set_settings_info(self.get_project_dir(), "submission_location", location)

	def get_user(self, username=None):
		'''
		returns a User object for the given username. If a username isn\'t given, the User object
		for the current user is returned.
		username -- (optional string) the username of the requested user
		'''
		return self._env.get_user(username)

	def get_current_username(self):
		'''
		returns the username of the current user
		'''
		return self._env.get_current_username()

	def get_asset(self, name):
		'''
		returns the asset object associated with the given name.
		name -- the name of the asset
		'''
		filepath = os.path.join(self._env.get_assets_dir(), name)
		if not os.path.exists(filepath):
			return None
		return Asset(filepath)

	def get_shot(self, name):
		'''
		returns the shot object associated with the given name.
		name -- the name of the shot
		'''
		filepath = os.path.join(self._env.get_assets_dir(), name)
		if not os.path.exists(filepath):
			return None
		return Shot(filepath)

	def get_tool(self, name):
		'''
		returns the tool object associated with the given name.
		name -- the name of the tool
		'''
		filepath = os.path.join(self._env.get_tools_dir(), name)
		if not os.path.exists(filepath):
			return None
		return Tool(filepath)

	def get_crowd_cycle(self, name):
		'''
		returns the crowd cycle object associated with the given name.
		name -- the name of the crowd cycle
		'''
		filepath = os.path.join(self._env.get_crowds_dir(), name)
		if not os.path.exists(filepath):
			return None
		return CrowdCycle(filepath)

	def get_body(self, name):
		'''
		returns the body object associated with the given name.
		name -- the name of the body
		'''
		body = self.get_asset(name)
		if body is None:
			body = self.get_tool(name)
		if body is None:
			body = self.get_crowd_cycle(name)
		return body

	def _create_body(self, name, bodyobj):
		'''
		If a body with that name already exists, raises EnvironmentError.
		The bodyobj is the class name for the body that will be created.
		'''
		name = pipeline_io.alphanumeric(name)
		print("name: ", name)
		filepath = os.path.join(bodyobj.get_parent_dir(), name)
		print("filepath: ", filepath)

		if name in self.list_bodies():
			# raise EnvironmentError('body already exists: '+filepath)
			return None  # body already exists

		if not pipeline_io.mkdir(filepath):
			raise OSError('couldn\'t create body directory: '+filepath)
			# some issue

		datadict = bodyobj.create_new_dict(name)
		pipeline_io.writefile(os.path.join(filepath, bodyobj.PIPELINE_FILENAME), datadict)
		new_body = bodyobj(filepath)
		for dept in self.default_departments():
			pipeline_io.mkdir(os.path.join(filepath, dept))
			new_body.create_element(dept, Element.DEFAULT_NAME)

		return new_body

	def create_asset(self, name, asset_type=AssetType.PROP):
		'''
		creates a new asset with the given name, and returns the resulting asset object.
		name -- the name of the new asset to create
		'''
		asset = self._create_body(name, Asset)

		if asset is None:
			return None  # asset already exists.

		asset.update_type(asset_type)

		if asset_type == str(AssetType.SHOT):
			rendered_shots = Environment().get_shots_dir()
			dir = os.path.join(rendered_shots, name)
			pipeline_io.mkdir(dir)

		return asset

	def create_shot(self, name):
		'''
		creates a new shot with the given name, and returns the resulting shot object.
		name -- the name of the new shot to create
		'''
		return self._create_body(name, Shot)

	def create_crowd_cycle(self, name):
		'''
		creates a new tool with the given name, and returns the resulting tool object.
		name -- the name of the new tool to create
		'''
		return self._create_body(name, CrowdCycle)

	def create_tool(self, name):
		'''
		creates a new tool with the given name, and returns the resulting tool object.
		name -- the name of the new tool to create
		'''
		return self._create_body(name, Tool)

	def _list_bodies_in_dir(self, filepath, filter=None):
		dirlist = os.listdir(filepath)

		bodylist = []
		for bodydir in dirlist:
			abspath = os.path.join(filepath, bodydir)
			if os.path.exists(os.path.join(abspath, Body.PIPELINE_FILENAME)):
				bodylist.append(bodydir)
			else:
				print("path doesn't exist?")
		bodylist.sort()

		if filter is not None and len(filter)==3:
			filtered_bodylist = []
			for body in bodylist:
				bodyobj = self.get_body(body)
				if bodyobj.has_relation(filter[0], filter[1], filter[2]):
					filtered_bodylist.append(body)
			bodylist = filtered_bodylist

		return bodylist

	def list_assets(self, filter=None):
		'''
		returns a list of strings containing the names of all assets in this project
		filter -- a tuple containing an attribute (string) relation (operator) and value
		          e.g. (Asset.TYPE, operator.eq, AssetType.ACTOR). Only returns assets whose
		          given attribute has the relation to the given desired value. Defaults to None.
		'''
		return self._list_bodies_in_dir(self._env.get_assets_dir(), filter)

	def list_shots(self, filter=None):
		'''
		returns a list of strings containing the names of all shots in this project
		filter -- a tuple containing an attribute (string) relation (operator) and value
				e.g. (Shot.FRAME_RANGE, operator.gt, 100). Only returns shots whose
				given attribute has the relation to the given desired value. Defaults to None.
		'''
		list = self.list_assets()

		shot_list = []

		for item in list:
			asset = self.get_asset(item)
			if asset.get_type() == AssetType.SHOT:
				shot_list.append(str(item))

		shot_list.sort(key=str.lower)

		return shot_list

	def list_tools(self):
		'''
		returns a list of strings containing the names of all tools in this project
		'''
		return self._list_bodies_in_dir(self._env.get_tools_dir())

	def list_hdas(self):
		'''
		returns a list of strings containing the names of all tools in this project
		'''
		hdas = os.listdir(self._env.get_hda_dir())
		names = []
		for hda in hdas:
			name, ext = os.path.splitext(hda)

			if not ext:
				continue

			if str(ext) == ".hda":
				names.append(name)

		return names

	def list_crowd_cycles(self):
		'''
		returns a list of strings containing the names of all crowds cycles in this project
		'''
		return self._list_bodies_in_dir(self._env.get_crowds_dir())

	def list_sets(self):
		'''
		returns a list of strings containing the names of all sets in this project
		'''
		list = self.list_assets()
		set_list = []

		for item in list:
			asset = self.get_asset(item)
			if asset.get_type() == AssetType.SET:
				set_list.append(str(item))

		set_list.sort(key=str.lower)

		return set_list

	def list_props_and_actors(self):
		'''
		returns a list of strings containing the names of all props/actors in this project
		'''
		pa_list = self.list_actors()
		pa_list.extend(self.list_props())

		pa_list.sort(key=str.lower)

		return pa_list

	def list_actors(self):
		list = self.list_assets()
		actors = []

		for item in list:
			asset = self.get_asset(item)
			if asset.get_type() == AssetType.ACTOR:
				actors.append(str(item))

		actors.sort(key=str.lower)

		return actors

	def list_props(self):
		list = self.list_assets()
		props = []

		for item in list:
			asset = self.get_asset(item)
			if asset.get_type() == AssetType.PROP:
				props.append(str(item))

		props.sort(key=str.lower)

		return props

	def list_bodies(self):
		'''
		returns a list of strings containing the names of all bodies (assets and shots)
		'''
		return self.list_assets() + self.list_shots() + self.list_tools() + self.list_crowd_cycles()

	def list_users(self):
		'''
		returns a list of strings containing the usernames of all users working on the project
		'''
		users_dir = self._env.get_users_dir()
		dirlist = os.listdir(users_dir)
		userlist = []
		for username in dirlist:
			userfile = os.path.join(users_dir, username, User.PIPELINE_FILENAME)
			if os.path.exists(userfile):
				userlist.append(username)
		userlist.sort()
		return userlist

	def list_bodies_by_departments(self, departments=Department.ALL):
		'''
		returns a list of tuples containing label and list of body names
		'''
		result = {}
		for department in departments:
			result[department] = []
		for body_name in self.list_bodies():
			for department in Department.ALL:
				body = self.get_body(body_name)
				try:
					if body and body.get_element(department):
						result[department].append(body.get_name())
				except Exception as e:
					pass
		return result

	def is_checkout_dir(self, path):
		'''
		returns True if the given path is a valid checkout directory
		returns False otherwise
		'''
		return os.path.exists(os.path.join(path, Checkout.PIPELINE_FILENAME))

	def get_checkout(self, path):
		'''
		returns the Checkout object describing the checkout operation at the given directory
		If the path is not a valid checkout directory, returns None
		'''
		if not self.is_checkout_dir(path):
			return None
		return Checkout(path)

	def get_checkout_element(self, path):
		'''
		returns the checked out element from the checkout operation at the given directory
		If the path is not a valid checkout directory, returns None
		'''
		checkout = self.get_checkout(path)
		if checkout is None:
			return checkout
		body = self.get_body(checkout.get_body_name())
		element = body.get_element(checkout.get_department_name(), checkout.get_element_name())
		return element

	def delete_shot(self, shot):
		'''
		delete the given shot
		'''
		if shot in self.list_shots():
			shutil.rmtree(os.path.join(self.get_shots_dir(), shot))

	def delete_asset(self, asset):
		'''
		delete the given asset
		'''
		if asset in self.list_assets():
			shutil.rmtree(os.path.join(self.get_asset_dir(), asset))

	def delete_tool(self, tool):
		'''
		delete the given tool
		'''
		if tool in self.list_tools():
			shutil.rmtree(os.path.join(self.get_tools_dir(), tool))

	def delete_crowd_cycle(self, crowd_cycle):
		'''
		delete the given crowd cycle
		'''
		if crowd_cycle in self.list_crowd_cycles():
			shutil.rmtree(os.path.join(self.get_crowds_dir(), crowd_cycle))

	def delete_ribs_for_bodies(self, bodies):
		for body in bodies:
			body = self.get_body(body)
			element = body.get_element(Department.RIB_ARCHIVE)

			rib_cache_dir = element.get_cache_dir()
			try:
				# delete the rib cache dir
				shutil.rmtree(rib_cache_dir)

			except:
				# create a new cache dir
				pipeline_io.mkdir(rib_cache_dir)


		print("deleted ribs for " + str(bodies))
