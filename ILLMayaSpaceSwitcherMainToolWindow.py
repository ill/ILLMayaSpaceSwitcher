import maya.cmds as cmds
import maya.mel as mel
from maya import OpenMayaUI as omui
# TODO: Figure out maya < 2025 and >= 2025 support
#from shiboken2 import wrapInstance
#from PySide2 import QtUiTools, QtCore, QtGui, QtWidgets
from shiboken6 import wrapInstance
from PySide6 import QtUiTools, QtCore, QtGui, QtWidgets
from functools import partial  # optional, for passing args during signal function calls
import sys
import pathlib


class ILLMayaSpaceSwitcherMainToolWindow(QtWidgets.QWidget):
    SETTINGS = QtCore.QSettings("ILLMayaSpaceSwitcher", "ILLMayaSpaceSwitcherMainToolWindow")
    GEOMETRY_SETTING = "geometry"

    INSTANCE = None

    @staticmethod
    def openMayaMainToolWindowInstance():
        print("Launching")

        if ILLMayaSpaceSwitcherMainToolWindow.INSTANCE is None or not ILLMayaSpaceSwitcherMainToolWindow.INSTANCE.isVisible():
            mayaMainWindowPtr = omui.MQtUtil.mainWindow()
            mayaMainWindow = wrapInstance(int(mayaMainWindowPtr), QtWidgets.QWidget)
            ILLMayaSpaceSwitcherMainToolWindow.INSTANCE = ILLMayaSpaceSwitcherMainToolWindow(parent=mayaMainWindow)
            ILLMayaSpaceSwitcherMainToolWindow.INSTANCE.setWindowTitle('Space Switcher')

        ILLMayaSpaceSwitcherMainToolWindow.INSTANCE.show()
        ILLMayaSpaceSwitcherMainToolWindow.INSTANCE.raise_()
        ILLMayaSpaceSwitcherMainToolWindow.INSTANCE.activateWindow()

    def __init__(self, parent=None):
        """
        Initialize class.
        """
        super(ILLMayaSpaceSwitcherMainToolWindow, self).__init__(parent=parent)
        self.setWindowFlags(QtCore.Qt.Window)
        self.widgetPath = str(pathlib.Path(__file__).parent.resolve())
        self.widget = QtUiTools.QUiLoader().load(self.widgetPath + '\\SpaceSwitcherManager.ui')
        self.widget.setParent(self)

        # set initial window sizes
        restoredGeometry = ILLMayaSpaceSwitcherMainToolWindow.SETTINGS.value(ILLMayaSpaceSwitcherMainToolWindow.GEOMETRY_SETTING, None)

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

        ILLMayaSpaceSwitcherMainToolWindow.SETTINGS.setValue(ILLMayaSpaceSwitcherMainToolWindow.GEOMETRY_SETTING, self.saveGeometry())

        if ILLMayaSpaceSwitcherMainToolWindow.INSTANCE == self:
            ILLMayaSpaceSwitcherMainToolWindow.INSTANCE = None

        self.destroy()

