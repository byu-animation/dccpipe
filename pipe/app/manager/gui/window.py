import sys
import os
try:
    from PySide import QtGui as QtWidgets
    from PySide import QtGui as QtGui
    from PySide import QtCore
    from PySide.QtCore import Slot, Signal, QObject
except ImportError:
    from PySide2 import QtWidgets, QtGui, QtCore
    from PySide2.QtCore import Slot, Signal, QObject

from resources import *
from pages import *
import viewmodel as ViewModel

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()

    def initialSize(self, percentage):
        dw = QtWidgets.QDesktopWidget()
        mainScreenSize = dw.availableGeometry(dw.primaryScreen())
        x = mainScreenSize.width() * percentage
        y = mainScreenSize.height() * percentage
        self.resize(x,y)

class ScreenLayout(QtWidgets.QStackedLayout):
    def __init__(self):
        super(ScreenLayout, self).__init__()
        self.pages = []
        self.setPages()
        for page in self.pages:
            self.addWidget(page)

    def setPages(self):
        self.pages.append(DashboardPage())
        for bodyType in PipelionResources().bodyTypes():
            self.pages.append(BodyOverviewPage(bodyType))
            for department in PipelionResources.departments(bodyType):
                self.pages.append(DepartmentPage(department))
        self.pages.append(SettingsPage())
        if(PipelionResources().isAdmin()):
            self.pages.append(AdminToolsPage())


class SideBarLink(QtWidgets.QLabel):

    clicked = Signal(int)

    def __init__(self, page, index):
        self.page = page
        self.index = index
        self.selected = (index == 0)
        super(SideBarLink, self).__init__(self.page.pageLabel)
        if self.page.isNestedPage:
            self.setObjectName("nested")

    def mousePressEvent(self, event):
        self.clicked.emit(self.index)
        self.selected = True

    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        if self.selected:
            painter.setBrush(QtGui.QBrush(QtGui.QColor.fromRgb(200,120,0,255)))
            painter.setPen(QtGui.QColor.fromRgb(0,0,0,0))
            painter.drawRect(0,0,self.width(),self.height())
        super(SideBarLink, self).paintEvent(event)

    def setSelected(self, selected):
        self.selected = selected
        self.update()


class SideBarLayout(QtWidgets.QVBoxLayout):
    def __init__(self, screenLayout):
        super(SideBarLayout, self).__init__()
        self.screenLayout = screenLayout
        self.links = []
        self.initialLayout()
        ViewModel.signals.changePage.connect(self.changePage)

    def initialLayout(self):
        self.setSpacing(0)
        self.addWidget(self.logoWidget(PipelionResources().logoSize()))
        count = 0
        for page in self.screenLayout.pages:
            linkWidget = SideBarLink(page, count)
            self.links.append(linkWidget)
            self.addWidget(linkWidget)
            linkWidget.clicked.connect(self.updateViews)
            count += 1
        self.addStretch()

    def updateViews(self, index):
        self.screenLayout.setCurrentIndex(index)
        for i in range(len(self.links)):
            self.links[i].setSelected(i == index)
        self.update()

    def logoWidget(self, size):
        logoImage = QtGui.QImage(PipelionResources().logo())
        logoWidget = QtWidgets.QLabel()
        logoWidget.setPixmap(QtGui.QPixmap.fromImage(logoImage).scaled(size,size))
        logoWidget.setObjectName("logo")
        return logoWidget

    @Slot(int, list)
    def changePage(self, index, bodies):
        self.updateViews(index)
