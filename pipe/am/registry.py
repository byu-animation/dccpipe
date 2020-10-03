# from .department import Department
from .element import Element
from .environment import Department


class Registry:
	"""
	Registry class to be used by shot and asset objects when creating element instances.
	Each department should define a factory method that will return the proper subclass of
	element for that department.
	"""

	def __init__(self):
		self._registrydict = {}
		self._registrydict[Department.DESIGN] = self.asset_element_factory
		self._registrydict[Department.MODEL] = self.maya_element_factory
		self._registrydict[Department.RIG] = self.maya_element_factory
		self._registrydict[Department.TEXTURE] = self.asset_element_factory
		self._registrydict[Department.MATERIAL] = self.hda_element_factory
		self._registrydict[Department.ASSEMBLY] = self.hda_element_factory
		self._registrydict[Department.LAYOUT] = self.maya_element_factory
		self._registrydict[Department.ANIM] = self.maya_element_factory
		self._registrydict[Department.CFX] = self.shot_element_factory
		self._registrydict[Department.FX] = self.shot_element_factory
		self._registrydict[Department.LIGHTING] = self.shot_element_factory
		self._registrydict[Department.RENDER] = self.shot_element_factory
		self._registrydict[Department.COMP] = self.shot_element_factory
		self._registrydict[Department.RENDER] = self.shot_element_factory
		self._registrydict[Department.HDA] = self.hda_element_factory
		self._registrydict[Department.CYCLES] = self.maya_element_factory
		self._registrydict[Department.RIB_ARCHIVE] = self.asset_element_factory
		self._registrydict[Department.MODIFY] = self.hda_element_factory
		self._registrydict[Department.HAIR] = self.sim_element_factory
		self._registrydict[Department.CLOTH] = self.sim_element_factory
		self._registrydict[Department.CAMERA] = self.element_factory

	def element_factory(self, filepath):
		return Element(filepath)

	def maya_element_factory(self, filepath):
		element = Element(filepath)
		element.set_app_ext(".mb")
		return element

	def hda_element_factory(self, filepath):
		element = Element(filepath)
		element.set_app_ext(".hdanc")
		return element

	'''
	FIXME: THESE ARE UNNECESSARY
	'''
	def asset_element_factory(self, filepath):
		return Element(filepath)

	def shot_element_factory(self, filepath):
		return Element(filepath)

	def sim_element_factory(self, filepath):
		return Element(filepath)

	# TODO: add factories for subclasses

	def create_element(self, department, filepath=None):
		"""
		create an object of the proper sublclass of element for the given department stored
		at the given filepath. If no filepath is given the resulting object will be empty.
		"""
		return self._registrydict[department](filepath)
