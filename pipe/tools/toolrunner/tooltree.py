#! /usr/bin/env python3
# from https://gist.github.com/skriticos/5415869
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# In this prototype/example a QTreeView is created. Then it's populated with
# three containers and all containers are populated with three rows, each
# containing three columns.
# Then the last container is expanded and the last row is selected.
# The container items are spanned through the all columns.
# Note: this requires > python-3.2
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
import sys, os, pprint, time
from Qt.QtWidgets import QTreeView
from Qt.QtGui import QAbstractItemView, QStandardItemModel, QStandardItem

class ToolTree(QTreeView):
    def __init__(self):
        super(ToolTree, self).__init__()
        self.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.model = QStandardItemModel()
        self.model.setHorizontalHeaderLabels(['col1', 'col2', 'col3'])
        self.setModel(self.model)
        self.setUniformRowHeights(True)

    def populate(self):
        for i in range(3):
            parent1 = QStandardItem('Family {}. Some long status text for sp'.format(i))
            for j in range(3):
                child1 = QStandardItem('Child {}'.format(i*3+j))
                child2 = QStandardItem('row: {}, col: {}'.format(i, j+1))
                child3 = QStandardItem('row: {}, col: {}'.format(i, j+2))
                parent1.appendRow([child1, child2, child3])

            self.model.appendRow(parent1)
            # span container columns
            self.setFirstColumnSpanned(i, view.rootIndex(), True)

        index = model.indexFromItem(parent1)
        self.expand(index)
        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        # select last row
        selmod = view.selectionModel()
        index2 = model.indexFromItem(child3)
        selmod.select(index2, QItemSelectionModel.Select|QItemSelectionModel.Rows)
        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
