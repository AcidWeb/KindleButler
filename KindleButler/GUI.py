# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'KindleButler.ui'
#
# Created: Sun Sep 28 14:52:18 2014
#      by: PyQt5 UI code generator 5.3.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(210, 40)
        MainWindow.setMinimumSize(QtCore.QSize(210, 40))
        MainWindow.setMaximumSize(QtCore.QSize(210, 40))
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/Icons/Assets/KindleButler.ico"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        MainWindow.setWindowIcon(icon)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.progressBar = QtWidgets.QProgressBar(self.centralwidget)
        self.progressBar.setGeometry(QtCore.QRect(5, 5, 200, 30))
        font = QtGui.QFont()
        font.setPointSize(13)
        font.setBold(True)
        font.setWeight(75)
        self.progressBar.setFont(font)
        self.progressBar.setAlignment(QtCore.Qt.AlignJustify|QtCore.Qt.AlignVCenter)
        self.progressBar.setObjectName("progressBar")
        MainWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "KindleButler"))
        self.progressBar.setFormat(_translate("MainWindow", "%p"))

from . import Resources
