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

    @staticmethod
    def open_maya_main_tool_window_instance():
        # QtWidgets.QApplication(sys.argv)
        maya_main_window_ptr = omui.MQtUtil.mainWindow()
        maya_main_window = wrapInstance(int(maya_main_window_ptr), QtWidgets.QWidget)
        window = ILLMayaSpaceSwitcherMainToolWindow(parent=maya_main_window)
        window.setWindowTitle('Space Switcher')
        window.show()

    def __init__(self, parent=None):
        """
        Initialize class.
        """
        super(ILLMayaSpaceSwitcherMainToolWindow, self).__init__(parent=parent)
        self.setWindowFlags(QtCore.Qt.Window)
        self.widgetPath = str(pathlib.Path(__file__).parent.resolve())
        self.widget = QtUiTools.QUiLoader().load(self.widgetPath + '\\SpaceSwitcherManager.ui')
        self.widget.setParent(self)

def thing():
    print("OPEN THE THING")
