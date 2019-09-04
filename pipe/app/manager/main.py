import os
import sys

import PySide2
try:
	from PySide import QtGui as QtWidgets
	from PySide import QtGui as QtGui
	from PySide import QtCore
except ImportError:
	from PySide2 import QtWidgets
	from PySide2 import QtGui
	from PySide2 import QtCore

import datetime
import operator

import pipe.gui.select_from_list as sfl
from pipe.am.body import AssetType, Asset, Shot
from pipe.am.environment import Department
from pipe.am.project import Project

# from byugui import request_email


class Status:
	ALL = ["one", "two"]

def get_status():
	return "one"

REF_WINDOW_WIDTH = 1080
REF_WINDOW_HEIGHT = 650

class TreeComboBoxItem(QtWidgets.QComboBox):

	def __init__(self, tree_item, column):
		QtWidgets.QComboBox.__init__(self)
		self.setFocusPolicy(QtCore.Qt.StrongFocus)
		self.tree_item = tree_item
		self.column = column
		self.currentIndexChanged.connect(self._change_item)

	def _change_item(self, index):
		self.tree_item.setText(self.column, self.itemText(index))

	def wheelEvent(self, e):
		e.ignore() # do nothing

	def paintEvent(self, pe):
		painter = QtGui.QPainter()
		painter.begin(self)
		pen = QtGui.QPen(QtCore.Qt.black)
		pen.setWidth(1)
		pen.setColor
		painter.setPen(pen)
		painter.drawRect(pe.rect())
		painter.end()

		QtWidgets.QComboBox.paintEvent(self, pe)

class TreeLineEdit(QtWidgets.QLineEdit):

	def __init__(self, contents, tree_item, column):
		QtWidgets.QLineEdit.__init__(self, contents)
		self.tree_item = tree_item
		self.column = column
		self.editingFinished.connect(self._change_item)

	def _change_item(self):
		self.tree_item.setText(self.column, self.text())

	def paintEvent(self, pe):
		painter = QtGui.QPainter()
		painter.begin(self)
		pen = QtGui.QPen(QtCore.Qt.black)
		pen.setWidth(1)
		pen.setColor
		painter.setPen(pen)
		painter.drawRect(pe.rect())
		painter.end()

		QtWidgets.QLineEdit.paintEvent(self, pe)

class TreeLabel(QtWidgets.QLabel):

	def __init__(self, text=""):
		QtWidgets.QLabel.__init__(self, text)
		self.setAutoFillBackground(True)

	def paintEvent(self, pe):
		painter = QtGui.QPainter()
		painter.begin(self)
		painter.setBrush(self.palette().color(QtGui.QPalette.AlternateBase))
		pen = QtGui.QPen(QtCore.Qt.black)
		pen.setWidth(1)
		pen.setColor
		painter.setPen(pen)
		painter.drawRect(pe.rect())
		painter.end()

		QtWidgets.QLabel.paintEvent(self, pe)

class TreeGridDelegate(QtWidgets.QStyledItemDelegate):

	def paint(self, painter, option, index):
		painter.save()
		# painter.setPen(option.palette.color(QtWidgets.QPalette.Text))
		painter.setPen(QtCore.Qt.black)
		painter.drawRect(option.rect)
		painter.restore()

		QtWidgets.QStyledItemDelegate.paint(self, painter, option, index)


class TreeDateEdit(QtWidgets.QWidget):

	def __init__(self, date, tree_item, column, parent=None, type='end'):
		QtWidgets.QDateEdit.__init__(self, parent)

		self.tree_item = tree_item
		self.column = column

		self.min_date = QtCore.QDate(2016,1,1)
		self.max_date = QtCore.QDate(2016,12,31)
		self.today = QtCore.QDate.currentDate()
		self.date_format = 'yyyy-MM-dd'
		self.date = date

		self.dateedit = TreeDateLineEdit(self)
		self.dateedit.setCalendarPopup(True)
		self.dateedit.setDisplayFormat(self.date_format)
		self.dateedit.setMinimumDate(self.min_date)
		self.dateedit.setMaximumDate(self.max_date)

		self.empty = DateLineEdit(date, self)

		self.layout = QtWidgets.QVBoxLayout(parent)
		self.layout.addWidget(self.empty)
		self.layout.addWidget(self.dateedit)

		if date!="":
			self.dateedit.setDate(QtCore.QDate.fromString(date, self.date_format))
			self.empty.setVisible(False)
			self.dateedit.setVisible(True)
		else:
			self.dateedit.setDate(self.today)
			self.empty.setVisible(True)
			self.dateedit.setVisible(False)

		self.setLayout(self.layout)
		self.empty.clicked.connect(self._show_date)
		self.dateedit.dateChanged.connect(self._change_date)

	def _show_date(self):
		self.dateedit.setVisible(True)
		# self.dateedit.setFocus(QtCore.Qt.OtherFocusReason)
		if self.date=="":
			self._change_date(self.today)

	def _change_date(self, date):
		self.date = date.toString(self.date_format)
		self.tree_item.setText(self.column, self.date)

	# def eventFilter(self, source, event):
	#	 if event.type() == QtCore.QEvent.FocusIn: #and source is self.empty
	#		 self._show_date()
	#	 return False


class TreeDateLineEdit(QtWidgets.QDateEdit):

	def __init__(self, parent=None):
		QtWidgets.QCalendarWidget.__init__(self, parent)

	def wheelEvent(self, e):
		e.ignore() # do nothing


class DateLineEdit(QtWidgets.QLineEdit):

	clicked = QtCore.Signal()

	def __init__(self, date="", parent=None):
		QtWidgets.QLineEdit.__init__(self, date, parent)

	def focusInEvent(self, event):
		QtWidgets.QLineEdit.focusInEvent(self, event)
		self.clicked.emit()


class ElementBrowser(QtWidgets.QWidget):

	ASSETS = "Assets"
	#SHOTS = "Shots"

	BODY_DATA_COLUMN = 1
	BODY_DESCRIPTION_COLUMN = 7

	@staticmethod
	def dark_palette():
		palette = QtGui.QPalette()
		base_color = QtGui.QColor(39,39,39)
		alt_color = QtGui.QColor(30,30,30)
		text_color = QtGui.QColor(192,192,192)
		highlight_color = QtGui.QColor(57,86,115)
		highlight_text_color = QtCore.Qt.white
		disabled_alt_color = QtGui.QColor(49,49,49)
		disabled_base_color = QtGui.QColor(40,40,40)
		disabled_text_color = QtGui.QColor(100,100,100)
		palette.setColor(QtGui.QPalette.Window, base_color)
		palette.setColor(QtGui.QPalette.WindowText, text_color)
		palette.setColor(QtGui.QPalette.Base, base_color)
		palette.setColor(QtGui.QPalette.AlternateBase, alt_color)
		palette.setColor(QtGui.QPalette.ToolTipBase, alt_color)
		palette.setColor(QtGui.QPalette.ToolTipText, text_color)
		palette.setColor(QtGui.QPalette.Button, base_color)
		palette.setColor(QtGui.QPalette.ButtonText, text_color)
		palette.setColor(QtGui.QPalette.Text, text_color)
		palette.setColor(QtGui.QPalette.Highlight, highlight_color)
		palette.setColor(QtGui.QPalette.HighlightedText, highlight_text_color)
		palette.setColor(QtGui.QPalette.Disabled, QtGui.QPalette.Window, disabled_base_color)
		palette.setColor(QtGui.QPalette.Disabled, QtGui.QPalette.WindowText, disabled_text_color)
		palette.setColor(QtGui.QPalette.Disabled, QtGui.QPalette.Base, disabled_text_color)
		palette.setColor(QtGui.QPalette.Disabled, QtGui.QPalette.AlternateBase, disabled_alt_color)
		palette.setColor(QtGui.QPalette.Disabled, QtGui.QPalette.Button, disabled_base_color)
		palette.setColor(QtGui.QPalette.Disabled, QtGui.QPalette.ButtonText, disabled_text_color)
		palette.setColor(QtGui.QPalette.Disabled, QtGui.QPalette.Text, disabled_text_color)
		return palette

	def __init__(self):
		QtWidgets.QWidget.__init__(self)
		self.setWindowTitle("Element Browser")
		self.setGeometry(0, 0, REF_WINDOW_WIDTH, REF_WINDOW_HEIGHT)
		self.palette = self.dark_palette()
		self.setPalette(self.palette)

		# initialize project
		self.project = Project()
		self.user_list = self.project.list_users()
		self.user_completer = QtWidgets.QCompleter(self.user_list)

		#filters
		self.filter_label = QtWidgets.QLabel("Filter by: ")

		self.dept_filter_label = QtWidgets.QLabel("Department")
		self.dept_filter_label.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
		self.dept_filter = QtWidgets.QComboBox()
		self.dept_filter.addItem("all")
		for each in Department.ALL:
			self.dept_filter.addItem(each)
		self.dept_list = Department.ALL

		self.type_filter_label = QtWidgets.QLabel("Asset Type")
		self.type_filter_label.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
		self.type_filter = QtWidgets.QComboBox()
		self.type_filter.addItem("all")
		for each in AssetType.ALL:
			self.type_filter.addItem(each)

		self.name_filter_label = QtWidgets.QLabel("Name")
		self.name_filter_label.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
		self.name_filter = QtWidgets.QLineEdit()

		# menu bar
		self.menu_bar = QtWidgets.QMenuBar()
		self.view_menu = QtWidgets.QMenu("View")
		self.menu_bar.addMenu(self.view_menu)
		self.expand_action = self.view_menu.addAction("Expand All")
		self.user_list_action = self.view_menu.addAction("User Directory")
		self.theme_action = self.view_menu.addAction("Default Theme")
		self.theme_action.setCheckable(True)

		# asset/shot menu
		self.body_menu = QtWidgets.QComboBox()
		self.body_menu.addItem(self.ASSETS)
		#self.body_menu.addItem(self.SHOTS)
		self.current_body = self.ASSETS
		self._set_bodies()

		# new button
		self.new_button = QtWidgets.QPushButton("New")

		# refresh button
		self.refresh_button = QtWidgets.QPushButton("Refresh")

		# tree
		self.tree = QtWidgets.QTreeWidget()
		self.tree.setItemDelegate(TreeGridDelegate(self.tree))
		self.columnCount = 8
		self.tree.setColumnCount(self.columnCount)
		tree_header = QtWidgets.QTreeWidgetItem(["name", "", "assigned", "status", "start", "end", "publish", "note"])
		self.tree.setHeaderItem(tree_header)
		tree_header_view = self.tree.header()
		tree_header_view.resizeSection(4, 120)
		tree_header_view.resizeSection(5, 120)

		self.init_tree = [None]*self.columnCount
		self.init_tree[0] = self.init_name
		self.init_tree[1] = self.init_dept
		self.init_tree[2] = self.init_assigned_user
		self.init_tree[3] = self.init_status
		self.init_tree[4] = self.init_start_date
		self.init_tree[5] = self.init_end_date
		self.init_tree[6] = self.init_last_publish
		self.init_tree[7] = self.init_note

		self._build_tree()

		self.update_tree = [None]*self.columnCount
		self.update_tree[0] = self.update_name
		self.update_tree[1] = self.update_dept
		self.update_tree[2] = self.update_assigned_user
		self.update_tree[3] = self.update_status
		self.update_tree[4] = self.update_start_date
		self.update_tree[5] = self.update_end_date
		self.update_tree[6] = self.update_last_publish
		self.update_tree[7] = self.update_note

		# status bar
		self.status_bar = QtWidgets.QStatusBar()

		# connect events
		self.expand_action.triggered.connect(self._expand_all)
		self.user_list_action.triggered.connect(self._show_user_directory)
		self.theme_action.triggered.connect(self._toggle_theme)
		self.body_menu.currentIndexChanged.connect(self._body_changed)
		self.new_button.clicked.connect(self._new_body)
		self.refresh_button.clicked.connect(self._refresh)
		self.tree.itemExpanded.connect(self._load_elements)
		self.tree.itemChanged.connect(self._item_edited)
		self.dept_filter.currentIndexChanged.connect(self._dept_filter_changed)
		self.name_filter.editingFinished.connect(self._filter_by_name)
		self.type_filter.currentIndexChanged.connect(self._refresh)

		# layout
		layout = QtWidgets.QVBoxLayout(self)
		layout.setSpacing(5)
		layout.setMargin(6)
		options_layout = QtWidgets.QGridLayout()
		options_layout.addWidget(self.body_menu, 0, 0)
		options_layout.addWidget(self.new_button, 0, 1)
		options_layout.addWidget(self.refresh_button, 0, 3)
		options_layout.setColumnMinimumWidth(0, 100)
		options_layout.setColumnMinimumWidth(1, 100)
		options_layout.setColumnMinimumWidth(3, 100)
		options_layout.setColumnStretch(2, 1)
		filter_layout = QtWidgets.QGridLayout()
		filter_layout.addWidget(self.filter_label, 0, 0)
		filter_layout.addWidget(self.dept_filter_label, 0, 1)
		filter_layout.addWidget(self.dept_filter, 0, 2)
		filter_layout.addWidget(self.name_filter_label, 0, 3)
		filter_layout.addWidget(self.name_filter, 0, 4)
		filter_layout.addWidget(self.type_filter_label, 0, 5)
		filter_layout.addWidget(self.type_filter, 0, 6)
		filter_layout.setColumnMinimumWidth(0, 50)
		filter_layout.setColumnMinimumWidth(1, 100)
		filter_layout.setColumnMinimumWidth(2, 100)
		filter_layout.setColumnMinimumWidth(3, 100)
		filter_layout.setColumnMinimumWidth(4, 100)
		filter_layout.setColumnMinimumWidth(5, 100)
		filter_layout.setColumnMinimumWidth(6, 100)

		filter_layout.setColumnStretch(7, 1)
		layout.addWidget(self.menu_bar)
		layout.addLayout(options_layout)
		layout.addWidget(self.tree)
		layout.addLayout(filter_layout)

		layout.addWidget(self.status_bar)
		self.setLayout(layout)

		# request_email.check_user_email(self)

	def _build_tree(self):
		self.tree.clear()
		tree_state = self.tree.blockSignals(True)
		for body in self.bodies:
			if(str(self.name_filter.text()) in body):
				tree_item = QtWidgets.QTreeWidgetItem([body])
				self.tree.addTopLevelItem(tree_item)
				tree_flags = tree_item.flags()
				tree_item.setFlags(tree_flags | QtCore.Qt.ItemIsEditable)
				# for col in xrange(self.columnCount):
				#	 tree_item.setBackground(col, QtWidgets.QColor(30,30,30))
				body_obj = self.project.get_body(body)
				self._load_body(body_obj, tree_item)
				tree_item.addChild(QtWidgets.QTreeWidgetItem()) # empty item
		self.tree.blockSignals(tree_state)

	def _load_body(self, body, item):
		tree_state = self.tree.blockSignals(True)
		item.setText(0, body.get_name())
		namelabel = TreeLabel(body.get_name())
		self.tree.setItemWidget(item, 0, namelabel)
		if self.current_body==self.ASSETS:
			body_type = body.get_type()
			item.setText(self.BODY_DATA_COLUMN, body_type)
			combobox = TreeComboBoxItem(item, self.BODY_DATA_COLUMN)
			type_idx = 0
			for idx, type in enumerate(AssetType.ALL):
				combobox.addItem(type)
				if type == body_type:
					type_idx = idx
			combobox.setCurrentIndex(type_idx)
			self.tree.setItemWidget(item, self.BODY_DATA_COLUMN, combobox)
		#elif self.current_body==self.SHOTS:
		#	item.setText(self.BODY_DATA_COLUMN, str(body.get_frame_range()))
		else:
			self.status_bar.showMessage("Error: unknown body type")

		description_edit = TreeLineEdit(body.get_description(), item, self.BODY_DESCRIPTION_COLUMN)
		self.tree.setItemWidget(item, self.BODY_DESCRIPTION_COLUMN, description_edit)

		for col in range(self.BODY_DATA_COLUMN+1, self.columnCount-1): # disable remaining columns
			emptylabel = TreeLabel()
			self.tree.setItemWidget(item, col, emptylabel)
		self.tree.blockSignals(tree_state)

	def _load_elements(self, item):
		tree_state = self.tree.blockSignals(True)
		body = str(item.text(0))
		body_obj = self.project.get_body(body)
		elements = []
		for dept in self.dept_list:
			dept_elements = body_obj.list_elements(dept)
			for dept_element in dept_elements:
				elements.append((dept, dept_element))
		item.takeChildren() # clear children
		for dept, element in elements:
			element_obj = body_obj.get_element(dept, element)
			child_item = QtWidgets.QTreeWidgetItem()
			item.addChild(child_item)
			child_item.setFlags(child_item.flags() | QtCore.Qt.ItemIsEditable)
			for col, init in enumerate(self.init_tree):
				init(element_obj, child_item, col)
		self.tree.blockSignals(tree_state)

	def _expand_all(self):
		# self.tree.expandAll()
		count = self.tree.topLevelItemCount()
		for i in xrange(count):
			item = self.tree.topLevelItem(i)
			self.tree.expandItem(item)

	def _show_user_directory(self):
		user_directory = UserListDialog(self)
		user_directory.show()

	def _toggle_theme(self):
		checked = self.theme_action.isChecked()
		if not checked:
			self.palette = self.dark_palette()
		else:
			self.palette = QtGui.QPalette()
		self.setPalette(self.palette)

	def _set_bodies(self):
		if self.current_body == self.ASSETS:
			asset_filter = None
			if(self.type_filter.currentIndex()):
				asset_filter_str = str(self.type_filter.currentText())
				asset_filter = (Asset.TYPE, operator.eq, asset_filter_str)
			self.bodies = self.project.list_assets(asset_filter)
		#elif self.current_body == self.SHOTS:
		#	self.bodies = self.project.list_shots()
		else:
			self.bodies = []

	def _item_edited(self, item, column):
		parent = item.parent()
		if parent is not None:
			body = str(parent.text(0))
			body_obj = self.project.get_body(body)
			element = str(item.text(0))
			dept = str(item.text(1))
			element_obj = body_obj.get_element(dept, element)
			self.update_tree[column](element_obj, item, column)
			# self.tree.resizeColumnToContents(column)
		else:
			body = str(item.text(0))
			body_obj = self.project.get_body(body)
			if column==self.BODY_DATA_COLUMN:
				self._update_body_data(body_obj, item)
			elif column==self.BODY_DESCRIPTION_COLUMN:
				self._update_body_description(body_obj, item)


	def _refresh(self): # TODO: maintain expanded rows on refresh
		self._set_bodies()
		self._build_tree()
		self.status_bar.clearMessage()

	def _body_changed(self, index):
		self.current_body = str(self.body_menu.itemText(index))
		if(self.body_menu.currentIndex()):
			self.type_filter.setEnabled(False)
			self.type_filter_label.setEnabled(False)
		else:
			self.type_filter.setEnabled(True)
			self.type_filter_label.setEnabled(True)
		self._refresh()

	def _dept_filter_changed(self):
		if(self.dept_filter.currentIndex()):
			self.dept_list = [str(self.dept_filter.currentText())]
		else:
			self.dept_list = Department.ALL
		self._refresh()

	def _filter_by_name(self):
		self._refresh()
		# target = str(self.name_filter.text())
		# for i in reversed(xrange(self.tree.topLevelItemCount())):
		#	 if (target not in self.tree.topLevelItem(i).text(0)):
		#		 self.tree.takeTopLevelItem(i)

	def _new_body(self):
		from byugui import new_body_gui
		self.new_body_dialog = new_body_gui.CreateWindow(self)
		if self.current_body == self.ASSETS:
			self.new_body_dialog.setCurrentIndex(self.new_body_dialog.ASSET_INDEX)
		#elif self.current_body == self.SHOTS:
		#	self.new_body_dialog.setCurrentIndex(self.new_body_dialog.SHOT_INDEX)
		self.new_body_dialog.finished.connect(self._refresh)

	def _update_body_data(self, body, item):
		if self.current_body==self.ASSETS:
			body.update_type(str(item.text(self.BODY_DATA_COLUMN)))
		#elif self.current_body==self.SHOTS:
		#	body.update_frame_range(int(item.text(self.BODY_DATA_COLUMN)))
		else:
			self.status_bar.showMessage("Error: unknown body type")

	def _update_body_description(self, body, item):
		body.update_description(str(item.text(self.BODY_DESCRIPTION_COLUMN)))

	def _valid_date(self, date):
		try:
			date_obj = datetime.datetime.strptime(date, "%Y-%m-%d").date()
			return str(date_obj)
		except ValueError:
			self.status_bar.showMessage(date+" not a valid date, please use format: YYYY-MM-DD")
			return None

	def init_name(self, element, item, column):
		item.setText(column, element.get_name())
		namelabel = TreeLabel(element.get_name())
		self.tree.setItemWidget(item, column, namelabel)

	def init_dept(self, element, item, column):
		item.setText(column, element.get_department())
		deptlabel = TreeLabel(element.get_department())
		self.tree.setItemWidget(item, column, deptlabel)

	def init_assigned_user(self, element, item, column):
		user = element.get_assigned_user()
		item.setText(column, user)
		lineedit = TreeLineEdit(user, item, column)
		lineedit.setCompleter(self.user_completer)
		self.tree.setItemWidget(item, column, lineedit)

	def init_status(self, element, item, column):
		item.setText(column, get_status())
		combobox = TreeComboBoxItem(item, column)
		element_type = get_status()
		type_idx = 0
		for idx, type in enumerate(Status.ALL):
			combobox.addItem(type)
			if type == element_type:
				type_idx = idx
		combobox.setCurrentIndex(type_idx)
		self.tree.setItemWidget(item, column, combobox)

	def init_start_date(self, element, item, column):
		start_date = element.get_start_date()
		item.setText(column, " "+start_date)
		start_dateedit = TreeDateEdit(start_date, item, column, self.tree)
		self.tree.setItemWidget(item, column, start_dateedit)

	def init_end_date(self, element, item, column):
		end_date = element.get_end_date()
		item.setText(column, " "+end_date)
		end_dateedit = TreeDateEdit(end_date, item, column, self.tree)
		self.tree.setItemWidget(item, column, end_dateedit)

	def init_last_publish(self, element, item, column):
		publish = element.get_last_publish()
		if publish is not None:
			item.setText(column, publish[0]+", "+publish[1]+", "+publish[2])
		else:
			item.setText(column, "")

	def init_note(self, element, item, column):
		item.setText(column, element.get_last_note())

	def update_name(self, element, item, column):
		self.status_bar.showMessage("can't change name")

	def update_dept(self, element, item, column):
		self.status_bar.showMessage("can't change department")

	def update_assigned_user(self, element, item, column):
		user = str(item.text(column))
		if user in self.user_list:
			element.update_assigned_user(user)
			self.status_bar.clearMessage()
		else:
			self.tree.itemWidget(item, column).setText(element.get_assigned_user())
			self.status_bar.showMessage('"' + user + '" is not a valid username')

	def update_status(self, element, item, column):
		# element.update_status(str(item.text(column)))
		self.status_bar.clearMessage()

	def update_start_date(self, element, item, column):
		date_str = str(item.text(column))
		valid_date_str = self._valid_date(date_str)
		if valid_date_str:
			element.update_start_date(valid_date_str)
			item.setText(column, " "+date_str)
			self.status_bar.clearMessage()
		else:
			self.init_start_date(element, item, column)

	def update_end_date(self, element, item, column):
		date_str = str(item.text(column))
		valid_date_str = self._valid_date(date_str)
		if valid_date_str:
			element.update_end_date(valid_date_str)
			item.setText(column, " "+date_str)
			self.status_bar.clearMessage()
		else:
			self.init_end_date(element, item, column)

	def update_last_publish(self, element, item, column):
		self.status_bar.showMessage("can't modify publish data")
		self.init_last_publish(element, item, column)

	def update_note(self, element, item, column):
		element.update_notes(str(item.text(column)))
		self.status_bar.clearMessage()

class UserListDialog(QtWidgets.QDialog):
	def __init__(self, parent):
		QtWidgets.QDialog.__init__(self, parent)
		self.setWindowTitle("User Directory")
		self.setPalette(parent.palette)
		user_count = len(parent.user_list)
		self.user_grid = QtWidgets.QTableWidget(user_count, 3, self)
		self.user_grid.verticalHeader().setVisible(False)
		self.user_grid.horizontalHeader().setVisible(False)

		self.user_info_list = []
		for username in parent.user_list:
			user_obj = parent.project.get_user(username)
			self.user_info_list.append((user_obj.get_fullname(), user_obj.get_username(), user_obj.get_email()))

		self.user_info_list.sort()

		for i, user_tuple in enumerate(self.user_info_list):
			for j, user_data in enumerate(user_tuple):
				table_item = QtWidgets.QTableWidgetItem(user_tuple[j])
				table_flags = table_item.flags()
				table_item.setFlags(table_flags & (~QtCore.Qt.ItemIsEditable))
				self.user_grid.setItem(i, j, table_item)
		self.user_grid.resizeColumnsToContents()

		self.layout = QtWidgets.QVBoxLayout()
		self.layout.addWidget(self.user_grid)
		self.setLayout(self.layout)

	def sizeHint(self):
		return QtCore.QSize(540, 800)

class Manager:

	def __init__(self):
		pass


	def go(self):
		print("here")
		print("sys.argv ", sys.argv)

		# try:
		# 	self.app = QtWidgets.QApplication(sys.argv)
		# except:
		# 	print("failed to create qapp")

		list = Status.ALL

		print("here 2")
		try:
			window = ElementBrowser()
		except Exception as e:
			print(e)

		print("here")  # fails between here and shown
		try:
			window.show()
		except Exception as e:
			print(e)

		print("shown")
		# sys.exit(app.exec_())

# if __name__ == '__main__':
# 	print("here")
# 	print("sys.argv ", sys.argv)
#
# 	try:
# 		self.app = QtWidgets.QApplication(sys.argv)
# 	except:
# 		print("failed to create qapp")
#
# 	list = Status.ALL
#
# 	print("here 2")
# 	window = ElementBrowser()
# 	print("here")
# 	window.show()
# 	sys.exit(app.exec_())
