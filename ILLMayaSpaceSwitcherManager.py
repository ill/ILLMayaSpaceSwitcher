# Add this to a shelf button to open the main UI
# import ILLMayaSpaceSwitcherManager
# ILLMayaSpaceSwitcherManager.ILLMayaSpaceSwitcherManager.openMayaMainToolWindowInstance()

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


class ILLMayaSpaceSwitcherManager(QtWidgets.QWidget):
    SETTINGS = QtCore.QSettings("ILLMayaSpaceSwitcher", "ILLMayaSpaceSwitcherManager")
    GEOMETRY_SETTING = "geometry"

    INSTANCE = None

    @staticmethod
    def openMayaMainToolWindowInstance():
        if ILLMayaSpaceSwitcherManager.INSTANCE is None or not ILLMayaSpaceSwitcherManager.INSTANCE.isVisible():
            mayaMainWindowPtr = omui.MQtUtil.mainWindow()
            mayaMainWindow = wrapInstance(int(mayaMainWindowPtr), QtWidgets.QWidget)
            ILLMayaSpaceSwitcherManager.INSTANCE = ILLMayaSpaceSwitcherManager(parent=mayaMainWindow)
            ILLMayaSpaceSwitcherManager.INSTANCE.setWindowTitle('Space Switcher')

        ILLMayaSpaceSwitcherManager.INSTANCE.show()
        ILLMayaSpaceSwitcherManager.INSTANCE.raise_()
        ILLMayaSpaceSwitcherManager.INSTANCE.activateWindow()

    @staticmethod
    def wipeSettings():
        ILLMayaSpaceSwitcherManager.SETTINGS.clear()
        ILLMayaSpaceSwitcherManager.SETTINGS.sync()

    def __init__(self, parent=None):
        """
        Initialize class.
        """
        super(ILLMayaSpaceSwitcherManager, self).__init__(parent=parent)
        self.setWindowFlags(QtCore.Qt.Window)
        self.widgetPath = str(pathlib.Path(__file__).parent.resolve())
        self.widget = QtUiTools.QUiLoader().load(self.widgetPath + '\\ILLMayaSpaceSwitcherManager.ui')
        self.widget.setParent(self)

        # set initial window sizes
        restoredGeometry = ILLMayaSpaceSwitcherManager.SETTINGS.value(ILLMayaSpaceSwitcherManager.GEOMETRY_SETTING, None)

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

        ILLMayaSpaceSwitcherManager.SETTINGS.setValue(ILLMayaSpaceSwitcherManager.GEOMETRY_SETTING, self.saveGeometry())

        if ILLMayaSpaceSwitcherManager.INSTANCE == self:
            ILLMayaSpaceSwitcherManager.INSTANCE = None

        self.destroy()

