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

import Util
import ILLMayaSpaceSwitcherModel

def createGroupNameWidget(groupName: str = None):
    widgetPath = str(pathlib.Path(__file__).parent.resolve())
    widget = QtUiTools.QUiLoader().load(widgetPath + '\\ILLMayaSpaceGroupNameWidget.ui')

    lbl_spaceGroupName: QtWidgets.QLabel = widget.findChild(QtWidgets.QLabel, 'lbl_spaceGroupName')
    lbl_spaceGroupName.setText(groupName)

    return widget

class IllMayaSpaceWidgetWrapper:
    def __init__(self, spaceName: str = None):
        widgetPath = str(pathlib.Path(__file__).parent.resolve())
        self.widget = QtUiTools.QUiLoader().load(widgetPath + '\\IllMayaSpaceWidget.ui')

        lbl_spaceName: QtWidgets.QLabel = self.widget.findChild(QtWidgets.QLabel, 'lbl_spaceName')
        lbl_spaceName.setText(spaceName)

class ILLMayaSpaceSwitcherManager(QtWidgets.QWidget):
    SETTINGS = QtCore.QSettings("ILLMayaSpaceSwitcher", "ILLMayaSpaceSwitcherManager")
    GEOMETRY_SETTING = "geometry"

    @staticmethod
    def openMayaMainToolWindowInstance():
        mayaMainWindowPtr = omui.MQtUtil.mainWindow()
        mayaMainWindow = wrapInstance(int(mayaMainWindowPtr), QtWidgets.QWidget)

        instance = ILLMayaSpaceSwitcherManager(parent=mayaMainWindow)
        instance.setWindowTitle('Space Switcher')

        instance.show()
        instance.raise_()
        instance.activateWindow()

        return instance

    @staticmethod
    def wipeSettings():
        ILLMayaSpaceSwitcherManager.SETTINGS.clear()
        ILLMayaSpaceSwitcherManager.SETTINGS.sync()

    def __init__(self, parent=None):
        """
        Initialize class.
        """
        super(ILLMayaSpaceSwitcherManager, self).__init__(parent=parent)

        self.selectedControls: list[str] = None
        self.spacesUnion: ILLMayaSpaceSwitcherModel.SpacesUnion() = None
        self.spaceWidgetWrappers: list[IllMayaSpaceWidgetWrapper] = None

        self.setWindowFlags(QtCore.Qt.Window)
        widgetPath = str(pathlib.Path(__file__).parent.resolve())
        self.widget = QtUiTools.QUiLoader().load(widgetPath + '\\ILLMayaSpaceSwitcherManager.ui')
        self.widget.setParent(self)

        # Refresh Button
        self.btn_refresh: QtWidgets.QPushButton = self.widget.findChild(QtWidgets.QPushButton, 'btn_refresh')
        self.btn_refresh.clicked.connect(self.refreshPressed)

        # Selected Control Label
        self.lbl_selectedControlsList: QtWidgets.QLabel = self.widget.findChild(QtWidgets.QLabel, 'lbl_selectedControlsList')

        # Key Enabled Check Box
        self.cb_keyEnabled: QtWidgets.QCheckBox = self.widget.findChild(QtWidgets.QCheckBox, 'cb_keyEnabled')

        # Auto Refresh Enabled Check Box
        self.cb_autoRefreshEnabled: QtWidgets.QCheckBox = self.widget.findChild(QtWidgets.QCheckBox, 'cb_autoRefreshEnabled')

        # Spaces List Contents
        self.sa_spacesListContents: QtWidgets.QWidget = self.widget.findChild(QtWidgets.QWidget, 'sa_spacesListContents')


        # set initial window geometry
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

        self.destroy()

    def refreshPressed(self):
        self.setSelectedControls(selectedControls=Util.getSelectedTransforms())

    def setSelectedControls(self, selectedControls:list[str]):
        if self.selectedControls == selectedControls:
            return

        self.selectedControls = selectedControls

        Util.clearWidget(self.sa_spacesListContents)
        self.spaceWidgetWrappers = None

        if self.selectedControls is None or len(self.selectedControls) <= 0:
            self.lbl_selectedControlsList.setText('None')
            return

        self.lbl_selectedControlsList.setText(', '.join([Util.getShortName(selectedControl) for selectedControl in self.selectedControls]))

        # go through each control and build the union of spaces
        self.spacesUnion = ILLMayaSpaceSwitcherModel.SpacesUnion()
        for spaces in [ILLMayaSpaceSwitcherModel.Spaces.fromControl(selectedControl) for selectedControl in self.selectedControls]:
            self.spacesUnion.addSpaces(spaces)

        self.spacesUnion.evaluateSpaces()

        self.spaceWidgetWrappers = []

        self.setupSpacesUI(spacesUnionGroup=self.spacesUnion.spacesUnionGroup, groupName="Spaces")
        self.setupSpacesUI(spacesUnionGroup=self.spacesUnion.rotationSpacesUnionGroup, groupName="Rotation Spaces")

    def setupSpacesUI(self, spacesUnionGroup: ILLMayaSpaceSwitcherModel.SpacesUnionGroup, groupName: str):
        # update the spaces UI
        if spacesUnionGroup is not None:
            if spacesUnionGroup.spaces is not None and len(spacesUnionGroup.spaces) > 0:
                self.sa_spacesListContents.layout().addWidget(createGroupNameWidget(groupName))

                for space in spacesUnionGroup.spaces:
                    spaceWidgetWrapper = IllMayaSpaceWidgetWrapper(spaceName=space.name)
                    self.sa_spacesListContents.layout().addWidget(spaceWidgetWrapper.widget)
                    self.spaceWidgetWrappers.append(spaceWidgetWrapper)
