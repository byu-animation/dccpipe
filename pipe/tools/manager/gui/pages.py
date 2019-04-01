import sys
import os
try:
    from PySide import QtGui as QtWidgets
    from PySide import QtGui as QtGui
    from PySide import QtCore
    from PySide.QtCore import Slot
except ImportError:
    from PySide2 import QtWidgets, QtGui, QtCore
    from PySide2.QtCore import Slot

from resources import *
from tables import *
import viewmodel as ViewModel
from programWidget import ProgramShelfWidget
from dialogs import CreateBodyController
from dialogs import *


class PageWidget(QtWidgets.QScrollArea):
    def __init__(self, pageLabel, isNestedPage=False):
        super(PageWidget, self).__init__()
        self.pageLabel = pageLabel
        self.isNestedPage = isNestedPage
        self.setSizePolicy(QtWidgets.QSizePolicy.MinimumExpanding, QtWidgets.QSizePolicy.MinimumExpanding)
        palette = QtGui.QPalette()
        palette.setColor(QtGui.QPalette.Background, QtGui.QColor("#c2cec7"))
        self.setAutoFillBackground(True)
        self.setPalette(palette)

    def headerWidget(self, label):
        banner = QtWidgets.QWidget()

        bannerText = QtWidgets.QLabel(label)
        bannerText.setAlignment(QtCore.Qt.AlignCenter)
        bannerLayout = QtWidgets.QHBoxLayout()
        bannerLayout.setMargin(0)
        bannerLayout.addWidget(bannerText)
        banner.setLayout(bannerLayout)

        banner.setStyleSheet('''
        background-color: #364441; padding: 10; font-size: 16px; color: white
        ''')
        banner.setSizePolicy(QtWidgets.QSizePolicy.MinimumExpanding, QtWidgets.QSizePolicy.Maximum)
        return banner

class DashboardPage(PageWidget):
    def __init__(self):
        super(DashboardPage, self).__init__(Strings.dashboard)
        ViewModel.signals.updateProduction.connect(self.updateData)
        self.setLayout(self.layoutPage())

    def layoutPage(self):
        pageLayout = QtWidgets.QVBoxLayout()
        pageLayout.addWidget(self.headerWidget(Strings.shortcuts))
        programs = PipelionResources.programs()
    	self.programShelfWidget = ProgramShelfWidget(programs, 100, 14, shortcuts=True)
        pageLayout.addWidget(self.programShelfWidget)
        pageLayout.addWidget(self.headerWidget(Strings.checkedoutitems))
        self.tableStack = QtWidgets.QStackedWidget()
        entries, headers = ViewModel.checkedOutTable()
        self.topBar = TableBar(ViewModel.checkedOutButtons())
        pageLayout.addWidget(self.topBar)
        noAssetView = QtWidgets.QLabel("You do not have anything checked out")
        noAssetView.setAlignment(QtCore.Qt.AlignCenter)
        self.tableStack.addWidget(noAssetView)
        self.table = Table(TableModel(entries, headers))
        if len(entries) > 0:
            self.topBar.setTable(self.table)
        self.tableStack.addWidget(self.table)
        self.tableStack.setCurrentIndex(1 if len(entries) > 0 else 0)
        pageLayout.addWidget(self.tableStack)
        return pageLayout

    @Slot(str)
    def updateData(self, str):
        entries, headers = ViewModel.checkedOutTable()
        self.tableStack.setCurrentIndex(1 if len(entries) > 0 else 0)
        self.table.setModel(TableModel(entries, headers))
        if len(entries) > 0:
            self.topBar.setTable(self.table)

        #self.tableStack.addWidget(table)
        self.update()



class SettingsPage(PageWidget):
    def __init__(self):
        super(SettingsPage, self).__init__(Strings.settings)
        self.setLayout(self.layoutPage())

    def layoutPage(self):
        pageLayout = QtWidgets.QHBoxLayout()
        pageLayout.addWidget(QtWidgets.QLabel("This is the settings page"))
        return pageLayout

class AdminToolsPage(PageWidget):
    def __init__(self):
        super(AdminToolsPage, self).__init__(Strings.admin_tools)
        self.setLayout(self.layoutPage())

    def layoutPage(self):
        pageLayout = QtWidgets.QHBoxLayout()
        pageLayout.addWidget(QtWidgets.QLabel("This is the admin tools page"))
        return pageLayout

class BodyOverviewPage(PageWidget):
    def __init__(self, bodyType):
        self.bodyType = bodyType
        super(BodyOverviewPage, self).__init__(self.bodyType[1])
        ViewModel.signals.updateProduction.connect(self.updateData)
        self.cbc = CreateBodyController(self.bodyType)
        self.setLayout(self.layoutPage())

    def layoutPage(self):
        pageLayout = QtWidgets.QVBoxLayout()
        hlayout = QtWidgets.QHBoxLayout()
        hlayout.addStretch()
        createButton = QtWidgets.QPushButton("Create " + self.bodyType[1])
        createButton.clicked.connect(self.cbc.showCreateBodyDialog)
        createButton.setSizePolicy(QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Maximum)
        createButton.setFixedHeight(60)
        createButton.setStyleSheet(Styles.createButton)
        hlayout.addWidget(createButton)
        hlayout.addStretch()
        pageLayout.addLayout(hlayout)
        self.tableStack = QtWidgets.QStackedWidget()
        entries, headers = ViewModel.bodyOverviewTable(self.bodyType)
        noAssetView = QtWidgets.QLabel("This is a body overview page for " + self.pageLabel)
        noAssetView.setAlignment(QtCore.Qt.AlignCenter)
        self.tableStack.addWidget(noAssetView)
        self.table = Table(TableModel(entries, headers))
        self.topBar = TableBar(ViewModel.bodyOverViewButtons(self.bodyType))
        pageLayout.addWidget(self.topBar)
        if len(entries) > 0:
            self.topBar.setTable(self.table)
        self.tableStack.addWidget(self.table)
        self.tableStack.setCurrentIndex(1 if len(entries) > 0 else 0)
        pageLayout.addWidget(self.tableStack)
        return pageLayout

    @Slot(str)
    def updateData(self, str):
        entries, headers = ViewModel.bodyOverviewTable(self.bodyType)
        self.tableStack.setCurrentIndex(1 if len(entries) > 0 else 0)
        self.table.setModel(TableModel(entries, headers))
        if len(entries) > 0:
            self.topBar.setTable(self.table)

        #self.tableStack.addWidget(table)
        self.update()


class DepartmentPage(PageWidget):
    def __init__(self, department):
        self.department = department
        super(DepartmentPage, self).__init__(self.department.name, isNestedPage=True)
        self.setLayout(self.layoutPage())

    def layoutPage(self):
        pageLayout = QtWidgets.QHBoxLayout()
        pageLayout.addWidget(QtWidgets.QLabel("This is a department page for " + self.pageLabel))
        return pageLayout
