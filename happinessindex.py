import sys
import os
from PyQt5 import QtCore
import pandas as pd
import glob
import json
from core import *
import numpy as np
from PyQt5.QtWidgets import QApplication, QWidget, QComboBox, QPushButton, QFileDialog, QVBoxLayout, QTableWidget, QTableWidgetItem


class PandasModel(QtCore.QAbstractTableModel):
    def __init__(self, df=pd.DataFrame(), parent=None):
        QtCore.QAbstractTableModel.__init__(self, parent=parent)
        self._df = df.copy()

    def toDataFrame(self):
        return self._df.copy()

    def headerData(self, section, orientation, role=QtCore.Qt.DisplayRole):
        if role != QtCore.Qt.DisplayRole:
            return QtCore.QVariant()

        if orientation == QtCore.Qt.Horizontal:
            try:
                return self._df.columns.tolist()[section]
            except (IndexError, ):
                return QtCore.QVariant()
        elif orientation == QtCore.Qt.Vertical:
            try:
                # return self.df.index.tolist()
                return self._df.index.tolist()[section]
            except (IndexError, ):
                return QtCore.QVariant()

    def data(self, index, role=QtCore.Qt.DisplayRole):
        if role != QtCore.Qt.DisplayRole:
            return QtCore.QVariant()

        if not index.isValid():
            return QtCore.QVariant()

        return QtCore.QVariant(str(self._df.ix[index.row(), index.column()]))

    def setData(self, index, value, role):
        row = self._df.index[index.row()]
        col = self._df.columns[index.column()]
        if hasattr(value, 'toPyObject'):
            # PyQt4 gets a QVariant
            value = value.toPyObject()
        else:
            # PySide gets an unicode
            dtype = self._df[col].dtype
            if dtype != object:
                value = None if value == '' else dtype.type(value)
        self._df.set_value(row, col, value)
        return True

    def rowCount(self, parent=QtCore.QModelIndex()):
        return len(self._df.index)

    def columnCount(self, parent=QtCore.QModelIndex()):
        return len(self._df.columns)

    def sort(self, column, order):
        colname = self._df.columns.tolist()[column]
        self.layoutAboutToBeChanged.emit()
        self._df.sort_values(colname, ascending=order == QtCore.Qt.AscendingOrder, inplace=True)
        self._df.reset_index(inplace=True, drop=True)
        self.layoutChanged.emit()


class MyApp(QWidget):
    def __init__(self):
        super().__init__()
        self.window_width, self.window_height = 800, 200
        self.setMinimumSize(self.window_width, self.window_height)
        self.files = []
        layout = QVBoxLayout()
        self.setLayout(layout)

        self.options = ('Single image processing', 'Batch processing')

        self.combo = QComboBox()
        self.combo.addItems(self.options)
        files = os.listdir('/home/danila/hindex/images')
        self.table = QTableWidget(self)  # Создаём таблицу
        self.inspectTable = QTableWidget(self)
        self.inspectTable.setColumnCount(2)
        self.inspectTable.setRowCount(8)
        self.inspectTable.setHorizontalHeaderLabels(["Emotion", "Probability"])
        self.table.setColumnCount(1)     # Устанавливаем три колонки
        self.table.setRowCount(1)        # и одну строку в таблице
        self.table.setHorizontalHeaderLabels(["Имя файла"])
        layout.addWidget(self.combo)
        layout.addWidget(self.table)
        btn = QPushButton('Select images to process')
        btn.clicked.connect(self.launchDialog)
        btn2 = QPushButton('Show processed images')
        btn3 = QPushButton('Inspect face')
        btn3.clicked.connect(self.showFace)
        btn2.clicked.connect(self.loadPredictionsList)
        layout.addWidget(btn)
        layout.addWidget(btn2)
        layout.addWidget(btn3)
        layout.addWidget(self.inspectTable)
        self.inspectTable.hide()


    def showFace(self):
        row = self.table.currentRow()
        fname = self.files[row].split('/')[-1]
        facepath = f'/home/danila/hindex/faces/{fname}.npy'
        with open(f'/home/danila/hindex/predictions/{fname}', 'r') as f:
            pred = json.load(f)
        img = np.load(facepath)
        self.inspectTable.clearContents()
        self.inspectTable.setRowCount(0)
        probs = pred['emotion']
        for k in sorted(probs, key=probs.get, reverse=True):
            row_number = self.inspectTable.rowCount()
            self.inspectTable.insertRow(row_number)
            self.inspectTable.setItem(row_number, 0, QTableWidgetItem(str(k)))
            self.inspectTable.setItem(row_number, 1, QTableWidgetItem(str(probs[k])))
        self.inspectTable.resizeColumnsToContents()
        self.inspectTable.show()
        cv2.imshow('Face: ' + facepath, img)

    def loadFilesList(self):
        files  = os.listdir('/home/danila/hindex/images')
        self.table.clearContents()
        self.table.setRowCount(0)
        for filename in files:
            row_number = self.table.rowCount()
            self.table.insertRow(row_number)
            self.table.setItem(row_number, 0, QTableWidgetItem(str(filename)))
        self.table.resizeColumnsToContents()

    def loadPredictionsList(self):
          self.files  = os.listdir('/home/danila/hindex/predictions')
          self.files.sort()
          i = 0
          self.table.clearContents()
          self.table.setRowCount(0)
          for filename in self.files:
              row_number = self.table.rowCount()
              self.table.insertRow(row_number)
              self.table.setItem(row_number, 0, QTableWidgetItem(str(filename)))
          self.table.resizeColumnsToContents()

    def launchDialog(self):
        option = self.options.index(self.combo.currentText())
        if option == 0:
            path = self.getFileName()
        elif option == 1:
            self.files = self.getFileNames()
            self.table.clearContents()
            self.table.setRowCount(0)
            for filename in self.files:
                row_number = self.table.rowCount()
                self.table.insertRow(row_number)
                self.table.setItem(row_number, 0, QTableWidgetItem(str(filename)))
            batch_process(self.files)

        else:
            print('Got Nothing')

    def getFileName(self):
        file_filter = 'Image files (*.png *.jpg *.jpeg);; Video files (*.mp4)'
        response = QFileDialog.getOpenFileName(
            parent=self,
            caption='Select a data file',
            directory='/home/danila/hindex/images',
            filter=file_filter,
            initialFilter='Image files (*.png *.jpg *.jpeg)'
        )
        print(response)
        return response[0]

    def getFileNames(self):
        file_filter = 'Image files (*.png *.jpg *.jpeg);; Video files (*.mp4)'
        response = QFileDialog.getOpenFileNames(
            parent=self,
            caption='Select a data file',
            directory='/home/danila/hindex/images',
            filter=file_filter,
            initialFilter='Image files (*.png *.jpg *.jpeg)'
        )
        return response[0]

    def getDirectory(self):
        response = QFileDialog.getExistingDirectory(
            self,
            caption='Select a folder'
        )
        return response

if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyleSheet('''
        QWidget {
            font-size: 35px;
        }
    ''')

    myApp = MyApp()
    myApp.show()

    try:
        sys.exit(app.exec_())
    except SystemExit:
        print('Closing Window...')
