# Add this to a shelf button to open the main UI
# import ILLMayaSpaceSwitcherConfiguration
# ILLMayaSpaceSwitcherConfiguration.ILLMayaSpaceSwitcherConfiguration.openMayaMainToolWindowInstance()

import maya.cmds as cmds
import maya.mel as mel
from maya import OpenMayaUI as omui
# TODO: Figure out maya < 2025 and >= 2025 support
# from shiboken2 import wrapInstance
# from PySide2 import QtUiTools, QtCore, QtGui, QtWidgets
from shiboken6 import wrapInstance
from PySide6 import QtUiTools, QtCore, QtGui, QtWidgets
from functools import partial  # optional, for passing args during signal function calls
import sys
import pathlib
import Util

class ILLMayaSpaceSwitcherConfiguration(QtWidgets.QWidget):
    SETTINGS = QtCore.QSettings("ILLMayaSpaceSwitcher", "ILLMayaSpaceSwitcherConfiguration")
    GEOMETRY_SETTING = "geometry"

    @staticmethod
    def openMayaMainToolWindowInstance():
        mayaMainWindowPtr = omui.MQtUtil.mainWindow()
        mayaMainWindow = wrapInstance(int(mayaMainWindowPtr), QtWidgets.QWidget)

        instance = ILLMayaSpaceSwitcherConfiguration(parent=mayaMainWindow)
        instance.setWindowTitle('Space Switcher Configuration')

        instance.show()
        instance.raise_()
        instance.activateWindow()

        return instance

    @staticmethod
    def wipeSettings():
        ILLMayaSpaceSwitcherConfiguration.SETTINGS.clear()
        ILLMayaSpaceSwitcherConfiguration.SETTINGS.sync()

    def __init__(self, parent=None):
        """
        Initialize class.
        """
        super(ILLMayaSpaceSwitcherConfiguration, self).__init__(parent=parent)

        self.selectedControl: str = None

        self.setWindowFlags(QtCore.Qt.Window)
        self.widgetPath = str(pathlib.Path(__file__).parent.resolve())
        self.widget = QtUiTools.QUiLoader().load(self.widgetPath + '\\ILLMayaSpaceSwitcherConfiguration.ui')
        self.widget.setParent(self)

        # set initial window sizes
        restoredGeometry = ILLMayaSpaceSwitcherConfiguration.SETTINGS.value(ILLMayaSpaceSwitcherConfiguration.GEOMETRY_SETTING, None)

        if restoredGeometry is None:
            self.resize(800, 480)
        else:
            try:
                self.restoreGeometry(restoredGeometry)
            except Exception as e:
                self.resize(800, 480)

        # Selected Control Label
        self.lbl_selectedControl: QtWidgets.QLabel = self.widget.findChild(QtWidgets.QLabel, 'lbl_selectedControl')

        # Refresh Button
        self.btn_refresh: QtWidgets.QPushButton = self.widget.findChild(QtWidgets.QPushButton, 'btn_refresh')
        self.btn_refresh.clicked.connect(self.refreshPressed)

        # Generate Default JSON Button
        self.btn_generateDefaultJsonContents: QtWidgets.QPushButton = self.widget.findChild(QtWidgets.QPushButton, 'btn_generateDefaultJsonContents')
        self.btn_generateDefaultJsonContents.clicked.connect(self.generateDefaultJsonContentsPressed)

        # JSON Contents Editor
        self.te_jsonContents: QtWidgets.QPlainTextEdit = self.widget.findChild(QtWidgets.QPlainTextEdit, 'te_jsonContents')

        # Set Space Configuration on Control Button
        self.btn_set: QtWidgets.QPushButton = self.widget.findChild(QtWidgets.QPushButton, 'btn_set')
        self.btn_set.clicked.connect(self.setPressed)

        # Get Selected Object Name Button
        self.btn_getSelectedObjectName: QtWidgets.QPushButton = self.widget.findChild(QtWidgets.QPushButton, 'btn_getSelectedObjectName')
        self.btn_getSelectedObjectName.clicked.connect(self.getSelectedObjectNamePressed)

        # Selection Name Line Edit
        self.le_selectionName: QtWidgets.QLineEdit = self.widget.findChild(QtWidgets.QLineEdit, 'le_selectionName')

    def resizeEvent(self, event):
        """
        Called on automatically generated resize event
        """
        self.widget.resize(self.width(), self.height())

    def closeEvent(self, event):
        """
        Close window.
        """

        ILLMayaSpaceSwitcherConfiguration.SETTINGS.setValue(ILLMayaSpaceSwitcherConfiguration.GEOMETRY_SETTING, self.saveGeometry())

        self.destroy()

    def refreshPressed(self):
        self.setSelectedControl(Util.getSelectedTransform())

    def generateDefaultJsonContentsPressed(self):
        print("Generate Default Contents")

    def setPressed(self):
        print("Set")

    def getSelectedObjectNamePressed(self):
        self.le_selectionName.setText(Util.getSelectedTransform())

    def setSelectedControl(self, selectedControl):
        self.selectedControl = selectedControl

        print("Setting selected control " + selectedControl)

        self.lbl_selectedControl.setText(Util.getShortName(self.selectedControl))