import os

# from .department import Department
from pipe.am.element import Element


from pipe.am.environment import Department, Environment
from pipe.am import pipeline_io
from pipe.am.registry import Registry

'''
body module
'''

class Body(object):
	'''
	Abstract class describing bodies that make up a project.
	'''
	# TODO allow users to subscribe to a body and recieve emails when changes are made
	PIPELINE_FILENAME = '.body'

	NAME = 'name'
	REFERENCES = 'references'
	DESCRIPTION = 'description'
	TYPE = 'type'
	FRAME_RANGE = 'frame_range'

	@staticmethod
	def create_new_dict(name):
		'''
		populate a dictionary with all the fields needed to create a new body
		'''
		datadict = {}
		datadict[Body.NAME] = name
		datadict[Body.REFERENCES] = []
		datadict[Body.DESCRIPTION] = ''
		datadict[Body.TYPE] = AssetType.PROP
		datadict[Body.FRAME_RANGE] = 0
		return datadict

	@staticmethod
	def get_parent_dir():
		'''
		return the parent directory that bodies of this type are stored in
		'''
		return Environment().get_assets_dir()

	def __init__(self, filepath):
		'''
		creates a Body instance describing the asset or shot stored in the given filepath
		'''
		self._env = Environment()
		self._filepath = filepath
		self._pipeline_file = os.path.join(filepath, Body.PIPELINE_FILENAME)
		if not os.path.exists(self._pipeline_file):
			raise EnvironmentError('not a valid body: ' + self._pipeline_file + ' does not exist')
		self._datadict = pipeline_io.readfile(self._pipeline_file)

	def __str__(self):
		name = self.get_name()
		filepath = self.get_filepath()
		type = self.get_type()

		return "<Body Object of TYPE " + str(type) + " with NAME " + str(name) + " AT " + str(filepath) + ">"

	def get_name(self):

		return self._datadict[Body.NAME]

	def get_filepath(self):
		return self._filepath

	def is_shot(self):
		if self.get_type() == AssetType.SHOT:
			return True
		else:
			return False

	def is_asset(self):
		return True

	def is_tool(self):

		raise NotImplementedError('subclass must implement is_tool')

	def is_crowd_cycle(self):

		raise NotImplementedError('subclass must implement is_crowd_cycle')

	def get_description(self):

		return self._datadict[Body.DESCRIPTION]

	def get_type(self):

		return self._datadict[Body.TYPE]

	def update_type(self, new_type):

		self._datadict[Body.TYPE] = new_type
		pipeline_io.writefile(self._pipeline_file, self._datadict)

	def get_frame_range(self):

		return self._datadict[Body.FRAME_RANGE]

	def set_frame_range(self, frame_range):
		self._datadict[Body.FRAME_RANGE] = frame_range

	def update_frame_range(self, frame_range):

		self._datadict[Body.FRAME_RANGE] = frame_range
		pipeline_io.writefile(self._pipeline_file, self._datadict)

	def get_latest_json_version(self, asset_name, department="model"):
		element = self.get_element(department)

		cache_dir = element.get_cache_dir()
		files = os.listdir(cache_dir)

		matches = []
		for file in files:
			root, ext = os.path.splitext(file)
			version = root[-1:]
			name = root[:-2]

			if str(name) == str(asset_name):
				# matches the asset
				matches.append([name, version, file])

		latest_version = 0
		latest_file = None
		for match in matches:
			if int(match[1]) >= latest_version:
				latest_version = int(match[1])
				latest_file = match[2]

		return latest_file, latest_version

	# def get_parent_dir(self):
	# 	'''
	# 	return the parent directory that bodies of this type are stored in
	# 	'''
	# 	raise NotImplementedError('subclass must implement get_parent_dir')

	def get_element(self, department, name=Element.DEFAULT_NAME, force_create=False):
		'''
		get the element object for this body from the given department. Raises EnvironmentError
		if no such element exists.
		department -- the department to get the element from
		name -- the name of the element to get. Defaults to the name of the
				element created by default for each department.
		'''
		element_dir = os.path.join(self._filepath, department, name)
		if not os.path.exists(element_dir):
			if force_create:
				try:
					self.create_element(department, name)
				except Exception as e:
					print(e)
			else:
				raise EnvironmentError('no such element: ' + element_dir + ' does not exist')

		return Registry().create_element(department, element_dir)

	def create_element(self, department, name):
		'''
		create an element for this body from the given department and return the
		resulting element object. Raises EnvironmentError if the element already exists.
		department -- the department to create the element for
		name -- the name of the element to create
		'''
		dept_dir = os.path.join(self._filepath, department)
		if not os.path.exists(dept_dir):
			pipeline_io.mkdir(dept_dir)
		name = pipeline_io.alphanumeric(name)
		element_dir = os.path.join(dept_dir, name)
		if not pipeline_io.mkdir(element_dir):
			raise EnvironmentError('element already exists: ' + element_dir)
		empty_element = Registry().create_element(department)
		datadict = empty_element.create_new_dict(name, department, self.get_name())
		pipeline_io.writefile(os.path.join(element_dir, empty_element.PIPELINE_FILENAME), datadict)
		return Registry().create_element(department, element_dir)

	def list_elements(self, department):
		'''
		return a list of all elements for the given department in this body
		'''
		subdir = os.path.join(self._filepath, department)
		if not os.path.exists(subdir):
			return []
		dirlist = os.listdir(subdir)
		elementlist = []
		for elementdir in dirlist:
			abspath = os.path.join(subdir, elementdir)
			if os.path.exists(os.path.join(abspath, Element.PIPELINE_FILENAME)):
				elementlist.append(elementdir)
		elementlist.sort()
		return elementlist

	def add_reference(self, reference):
		'''
		Add the given reference to this body. If it already exists, do nothing. If reference is not a valid
		body, raise an EnvironmentError.
		'''
		ref_asset_path = os.path.join(self._env.get_assets_dir(), reference, Body.PIPELINE_FILENAME)
		ref_shot_path = os.path.join(self._env.get_shots_dir(), reference, Body.PIPELINE_FILENAME)
		ref_crowd_path = os.path.join(self._env.get_crowds_dir(), reference, Body.PIPELINE_FILENAME)
		if not os.path.exists(ref_asset_path) and not os.path.exists(ref_shot_path) and not os.path.exists(ref_crowd_path):
			raise EnvironmentError(reference + ' is not a valid body')
		if reference not in self._datadict[Body.REFERENCES]:
			self._datadict[Body.REFERENCES].append(reference)
		pipeline_io.writefile(self._pipeline_file, self._datadict)

	def remove_reference(self, reference):
		'''
		Remove the given reference, if it exists, and return True. Otherwise do nothing, and return False.
		'''
		try:
			self._datadict[Body.REFERENCES].remove(reference)
			return True
		except ValueError:
			return False
		pipeline_io.writefile(self._pipeline_file, self._datadict)

	def update_description(self, description):

		self._datadict[Body.DESCRIPTION] = description
		pipeline_io.writefile(self._pipeline_file, self._datadict)

	def get_references(self):
		'''
		Return a list of all references for this body.
		'''
		return self._datadict[Body.REFERENCES]

	def has_relation(self, attribute, relate, value):
		'''
		Return True if this body has the given attribute and if the given relationship
		to the the given value. Return False otherwise
		'''
		if attribute not in self._datadict:
			return False
		return relate(self._datadict[attribute],value)

class AssetType:
	'''
	Class describing types of assets.
	'''

	ACTOR = 'actor'
	SET = 'set'
	PROP = 'prop'
	TOOL = 'tool'
	SHOT = 'shot'
	ALL = [ACTOR, PROP, SET, SHOT, TOOL]
	MAYA = [ACTOR, PROP, SET, SHOT]

	def __init__(self):
		pass

	def list_asset_types(self):
		return self.ALL

	def list_maya_types(self):
		return self.MAYA

class Asset(Body):
	'''
	Class describing an asset body.
	'''

	@staticmethod
	def create_new_dict(name):
		datadict = Body.create_new_dict(name)
		return datadict

	def __str__(self):
		return super(Asset, self).__str__()

	def is_tool(self):
		return False

	def is_crowd_cycle(self):
		return False


class Shot(Body):
	'''
	Class describing a shot body.
	'''

	@staticmethod
	def create_new_dict(name):
		datadict = Body.create_new_dict(name)
		return datadict

	def __str__(self):
		return super(Shot, self).__str__()

	def is_tool(self):
		return False

	def is_crowd_cycle(self):
		return False


class Tool(Body):
	'''
	Class describing a tool body.
	'''

	@staticmethod
	def create_new_dict(name):

		datadict = Body.create_new_dict(name)
		return datadict

	def __str__(self):
		return super(Tool, self).__str__()

	def is_shot(self):

		return False

	def is_asset(self):

		return False

	def is_tool(self):

		return True

	def is_crowd_cycle(self):

		return False

class CrowdCycle(Body):
	'''
	Class describing a tool body.
	'''

	@staticmethod
	def create_new_dict(name):

		datadict = Body.create_new_dict(name)
		return datadict

	def __str__(self):
		return super(CrowdCycle, self).__str__()

	def is_shot(self):

		return False

	def is_asset(self):

		return False

	def is_tool(self):

		return False

	def is_crowd_cycle(self):

		return True
