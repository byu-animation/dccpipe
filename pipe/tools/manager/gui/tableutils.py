#!/usr/bin/python

import operator
import sys
import os
try:
    from PySide import QtGui as QtWidgets
    from PySide import QtGui as QtGui
    from PySide import QtCore
    from PySide.QtCore import Slot, SIGNAL
except ImportError:
    from PySide2 import QtWidgets, QtGui, QtCore
    from PySide2.QtCore import Slot, SIGNAL

# TODO: setIndexWidget for any data that is a button
# https://stackoverflow.com/questions/4412796/qt-qtableview-clickable-button-in-table-row

class TableUtils():
    # Get assets from departments
    def __init__(self):
        self.thing = 0

class AssetEntry():
    def __init__(self, label, user, steps, notes):
        self.label = label
        self.user = user
        self.steps = steps
        self.notes = notes

class AssetTable(QtWidgets.QTableWidget):
    # int, int, string[], AssetEntry[]
    def __init__(self, rowCount, columnCount, columnHeaders, assetEntries):
        QtWidgets.QTableView.__init__(self, rowCount, columnCount)

        self.setHorizontalHeaderLabels(columnHeaders)

        for i in range(0,rowCount):
            for j in range(0, columnCount):
                entry = assetEntries[i]
                widget = QtWidgets.QLabel("error")
                if j == 0:
                    widget = QtWidgets.QLabel(entry.label)
                if j == 1:
                    widget = QtWidgets.QLabel(entry.user)
                if j > 1 and j < columnCount - 1:
                    widget = QtWidgets.QCheckBox()
                    widget.setChecked(entry.steps[j])
                if j == columnCount - 1:
                    widget = QtWidgets.QLineEdit(entry.notes)
                self.setCellWidget(i, j, widget)


class TableContainer(QtWidgets.QWidget):
    def __init__(self, data_list, header, *args):
        QtWidgets.QWidget.__init__(self, *args)
        # setGeometry(x_pos, y_pos, width, height)
        #self.setGeometry(300, 200, 570, 450)
        self.setWindowTitle("Click on column title to sort")
        table = QtWidgets.QTableWidget()
        # set font
        font = QtGui.QFont("Courier New", 10)
        table.setFont(font)
        # set column width to fit contents (set font first!)
        table.setRowCount(len(data_list))
        table.setColumnCount(len(header))
        table.verticalHeader().setVisible(False)
        table.setHorizontalHeaderLabels(header)
        for row in range(len(data_list)):
            table.setItem(row,0,QtWidgets.QTableWidgetItem(str(data_list[row][0])))
            table.setItem(row,1,QtWidgets.QTableWidgetItem(",".join(data_list[row][1])))
            table.setCellWidget(row,2,QtWidgets.QPushButton("Open"))
            if data_list[row][3]:
                table.setCellWidget(row,3,QtWidgets.QPushButton("Sync Now"))
            else:
                table.setItem(row,3,QtWidgets.QTableWidgetItem("Up to date"))
            table.setItem(row,4,QtWidgets.QTableWidgetItem(str(data_list[row][4]) + " kb"))
            table.setCellWidget(row,5,QtWidgets.QPushButton("Delete"))
        table.resizeColumnsToContents()
        # enable sorting
        table.setSortingEnabled(True)
        layout = QtWidgets.QVBoxLayout(self)
        layout.addWidget(table)
        self.setLayout(layout)

class TableDeptContainer(QtWidgets.QWidget):
    def __init__(self, data_list, header, *args):
        QtWidgets.QWidget.__init__(self, *args)
        # setGeometry(x_pos, y_pos, width, height)
        #self.setGeometry(300, 200, 570, 450)
        self.setWindowTitle("Click on column title to sort")
        table = QtWidgets.QTableWidget()
        # set font
        font = QtGui.QFont("Courier New", 10)
        table.setFont(font)
        # set column width to fit contents (set font first!)
        table.setRowCount(len(data_list))
        table.setColumnCount(len(header))
        table.verticalHeader().setVisible(False)
        table.setHorizontalHeaderLabels(header)
        for row in range(len(data_list)):
            table.setItem(row,0,QtWidgets.QTableWidgetItem(str(data_list[row][0])))
            table.setItem(row,1,QtWidgets.QTableWidgetItem(str(data_list[row][1])))
            button = QtWidgets.QPushButton("View")
            button.setEnabled(data_list[row][2])
            table.setCellWidget(row,2,button)
            table.setCellWidget(row,3,QtWidgets.QPushButton(str(data_list[row][3])))
        table.resizeColumnsToContents()
        # enable sorting
        table.setSortingEnabled(True)
        layout = QtWidgets.QVBoxLayout(self)
        layout.addWidget(table)
        self.setLayout(layout)

class TableModel(QtCore.QAbstractTableModel):
    def __init__(self, parent, mylist, header, *args):
        QtCore.QAbstractTableModel.__init__(self, parent, *args)
        self.mylist = mylist
        self.header = header
    def rowCount(self, parent):
        return len(self.mylist)
    def columnCount(self, parent):
        return len(self.mylist[0])
    def data(self, index, role):
        if not index.isValid():
            return None
        elif role != QtCore.Qt.DisplayRole:
            return None
        combobox = QtWidgets.QComboBox()
        combobox.addItem(str(self.mylist[index.row()][index.column()]))
        return str(self.mylist[index.row()][index.column()])
    def headerData(self, col, orientation, role):
        if orientation == QtCore.Qt.Horizontal and role == QtCore.Qt.DisplayRole:
            return self.header[col]
        return None
    def sort(self, col, order):
        """sort table by given column number col"""
        self.emit(SIGNAL("layoutAboutToBeChanged()"))
        self.mylist = sorted(self.mylist,
            key=operator.itemgetter(col))
        if order == QtCore.Qt.DescendingOrder:
            self.mylist.reverse()
        self.emit(SIGNAL("layoutChanged()"))

class DefaultData():
    def __init__(self):
        self.headers = self.headers()
        self.data = self.data()
    def headers(self):
        # the solvent data ...
        return ['Solvent Name', ' BP (deg C)', ' MP (deg C)', ' Density (g/ml)']
    def data(self):
        return [
        ('ACETIC ACID', 117.9, 16.7, 1.049),
        ('ACETIC ANHYDRIDE', 140.1, -73.1, 1.087),
        ('ACETONE', 56.3, -94.7, 0.791),
        ('ACETONITRILE', 81.6, -43.8, 0.786),
        ('ANISOLE', 154.2, -37.0, 0.995),
        ('BENZYL ALCOHOL', 205.4, -15.3, 1.045),
        ('BENZYL BENZOATE', 323.5, 19.4, 1.112),
        ('BUTYL ALCOHOL NORMAL', 117.7, -88.6, 0.81),
        ('BUTYL ALCOHOL SEC', 99.6, -114.7, 0.805),
        ('BUTYL ALCOHOL TERTIARY', 82.2, 25.5, 0.786),
        ('CHLOROBENZENE', 131.7, -45.6, 1.111),
        ('CYCLOHEXANE', 80.7, 6.6, 0.779),
        ('CYCLOHEXANOL', 161.1, 25.1, 0.971),
        ('CYCLOHEXANONE', 155.2, -47.0, 0.947),
        ('DICHLOROETHANE 1 2', 83.5, -35.7, 1.246),
        ('DICHLOROMETHANE', 39.8, -95.1, 1.325),
        ('DIETHYL ETHER', 34.5, -116.2, 0.715),
        ('DIMETHYLACETAMIDE', 166.1, -20.0, 0.937),
        ('DIMETHYLFORMAMIDE', 153.3, -60.4, 0.944),
        ('DIMETHYLSULFOXIDE', 189.4, 18.5, 1.102),
        ('DIOXANE 1 4', 101.3, 11.8, 1.034),
        ('DIPHENYL ETHER', 258.3, 26.9, 1.066),
        ('ETHYL ACETATE', 77.1, -83.9, 0.902),
        ('ETHYL ALCOHOL', 78.3, -114.1, 0.789),
        ('ETHYL DIGLYME', 188.2, -45.0, 0.906),
        ('ETHYLENE CARBONATE', 248.3, 36.4, 1.321),
        ('ETHYLENE GLYCOL', 197.3, -13.2, 1.114),
        ('FORMIC ACID', 100.6, 8.3, 1.22),
        ('HEPTANE', 98.4, -90.6, 0.684),
        ('HEXAMETHYL PHOSPHORAMIDE', 233.2, 7.2, 1.027),
        ('HEXANE', 68.7, -95.3, 0.659),
        ('ISO OCTANE', 99.2, -107.4, 0.692),
        ('ISOPROPYL ACETATE', 88.6, -73.4, 0.872),
        ('ISOPROPYL ALCOHOL', 82.3, -88.0, 0.785),
        ('METHYL ALCOHOL', 64.7, -97.7, 0.791),
        ('METHYL ETHYLKETONE', 79.6, -86.7, 0.805),
        ('METHYL ISOBUTYL KETONE', 116.5, -84.0, 0.798),
        ('METHYL T-BUTYL ETHER', 55.5, -10.0, 0.74),
        ('METHYLPYRROLIDINONE N', 203.2, -23.5, 1.027),
        ('MORPHOLINE', 128.9, -3.1, 1.0),
        ('NITROBENZENE', 210.8, 5.7, 1.208),
        ('NITROMETHANE', 101.2, -28.5, 1.131),
        ('PENTANE', 36.1, ' -129.7', 0.626),
        ('PHENOL', 181.8, 40.9, 1.066),
        ('PROPANENITRILE', 97.1, -92.8, 0.782),
        ('PROPIONIC ACID', 141.1, -20.7, 0.993),
        ('PROPIONITRILE', 97.4, -92.8, 0.782),
        ('PROPYLENE GLYCOL', 187.6, -60.1, 1.04),
        ('PYRIDINE', 115.4, -41.6, 0.978),
        ('SULFOLANE', 287.3, 28.5, 1.262),
        ('TETRAHYDROFURAN', 66.2, -108.5, 0.887),
        ('TOLUENE', 110.6, -94.9, 0.867),
        ('TRIETHYL PHOSPHATE', 215.4, -56.4, 1.072),
        ('TRIETHYLAMINE', 89.5, -114.7, 0.726),
        ('TRIFLUOROACETIC ACID', 71.8, -15.3, 1.489),
        ('WATER', 100.0, 0.0, 1.0),
        ('XYLENES', 139.1, -47.8, 0.86)
        ]

class DefaultUserData():
    def __init__(self):
        self.headers = self.headers()
        self.data = self.data()
    def headers(self):
        # the solvent data ...
        return ['My Checked out Items', 'Checked out by', 'Open', 'Sync', '', 'Delete']
    def data(self):
        return [
        ('house/interior/hallway', ['htinney', 'csivek'], '', True, 1494408, ''),
        ('house/interior/hallway', ['htinney'], '', True, 232408, ''),
        ('global/leaves/leaf002', ['htinney'], '', False, 42, ''),
        ('shots/c/004', ['htinney', 'kgraham','bdemann','csivek'], '', False, 12500408, '')
        ]

class DefaultDeptData():
    def __init__(self, department):
        self.headers = self.headers()
        self.data = self.data(department)
    def headers(self):
        # the solvent data ...
        return ['Asset Name', 'Assigned Artist', 'View', 'Action']
    def data(self, department):
        if (department == "model"):
            return [
            ('office/interior/chair', 'htinney', True, 'OPEN'),
            ('office/interior/computer', 'csivek', True, 'CHECK_OUT'),
            ('house/interior/pictureframes', 'kgraham', False, 'CREATE'),
            ]
        elif (department == "rig"):
            return [
            ('delilah', 'csivek', True, 'CHECK_OUT'),
            ('death/pen', 'bdemann', True, 'CHECK_OUT'),
            ]
        elif (department == "concept"):
            return [
            ('house/interior', 'kendrag', True, 'CHECK_OUT'),
            ('house/interior/hallway', 'bdemann', False, 'CREATE'),
            ('global/leaves', 'kendrag', True, 'CHECK_OUT'),
            ]
        elif (department == "material"):
            return [
            ('house/interior/hallway/floor', 'htinney', False, 'CREATE'),
            ('office/interior/chair', 'csivek', True, 'CHECK_OUT'),
            ]
        elif (department == "groom"):
            return [
            ('delilah/hair', 'htinney', True, 'OPEN'),
            ]
        else:
            return []
