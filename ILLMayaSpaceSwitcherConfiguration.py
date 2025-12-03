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


class ILLMayaSpaceSwitcherConfiguration(QtWidgets.QWidget):
    SETTINGS = QtCore.QSettings("ILLMayaSpaceSwitcher", "ILLMayaSpaceSwitcherConfiguration")
    GEOMETRY_SETTING = "geometry"

    INSTANCE = None

    @staticmethod
    def openMayaMainToolWindowInstance():
        print("Launching")

        if ILLMayaSpaceSwitcherConfiguration.INSTANCE is None or not ILLMayaSpaceSwitcherConfiguration.INSTANCE.isVisible():
            mayaMainWindowPtr = omui.MQtUtil.mainWindow()
            mayaMainWindow = wrapInstance(int(mayaMainWindowPtr), QtWidgets.QWidget)
            ILLMayaSpaceSwitcherConfiguration.INSTANCE = ILLMayaSpaceSwitcherConfiguration(parent=mayaMainWindow)
            ILLMayaSpaceSwitcherConfiguration.INSTANCE.setWindowTitle('Space Switcher Configuration')

        ILLMayaSpaceSwitcherConfiguration.INSTANCE.show()
        ILLMayaSpaceSwitcherConfiguration.INSTANCE.raise_()
        ILLMayaSpaceSwitcherConfiguration.INSTANCE.activateWindow()

    @staticmethod
    def wipeSettings():
        ILLMayaSpaceSwitcherConfiguration.SETTINGS.clear()
        ILLMayaSpaceSwitcherConfiguration.SETTINGS.sync()

    def __init__(self, parent=None):
        """
        Initialize class.
        """
        super(ILLMayaSpaceSwitcherConfiguration, self).__init__(parent=parent)
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

        if ILLMayaSpaceSwitcherConfiguration.INSTANCE == self:
            ILLMayaSpaceSwitcherConfiguration.INSTANCE = None

        self.destroy()

