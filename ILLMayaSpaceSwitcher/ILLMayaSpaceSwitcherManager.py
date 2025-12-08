# Add this to a shelf button to open the main UI
# import ILLMayaSpaceSwitcherManager
# ILLMayaSpaceSwitcherManager.ILLMayaSpaceSwitcherManager.openMayaMainToolWindowInstance()

from maya import OpenMayaUI as omui
# TODO: Figure out maya < 2025 and >= 2025 support
# from shiboken2 import wrapInstance
# from PySide2 import QtUiTools, QtCore, QtGui, QtWidgets
from shiboken6 import wrapInstance
from PySide6 import QtUiTools, QtCore, QtGui, QtWidgets
import pathlib

import Util
import ILLMayaSpaceSwitcherModel

def createGroupNameWidget(groupName: str = None):
    widget = QtUiTools.QUiLoader().load(Util.PACKAGE_DIR / 'ILLMayaSpaceGroupNameWidget.ui')

    lbl_spaceGroupName: QtWidgets.QLabel = widget.findChild(QtWidgets.QLabel, 'lbl_spaceGroupName')
    lbl_spaceGroupName.setText(groupName)

    return widget

class IllMayaSpaceWidgetWrapper:
    def __init__(self, parentManager, space: ILLMayaSpaceSwitcherModel.SpacesIntersectionSpace):
        self.widget = QtUiTools.QUiLoader().load(Util.PACKAGE_DIR / 'IllMayaSpaceWidget.ui')

        self.parentManager = parentManager
        self.space = space

        self.lbl_spaceName: QtWidgets.QLabel = self.widget.findChild(QtWidgets.QLabel, 'lbl_spaceName')
        self.lbl_spaceName.setText(space.name)

        self.btn_switchToSpace: QtWidgets.QPushButton = self.widget.findChild(QtWidgets.QPushButton, 'btn_switchToSpace')
        self.btn_switchToSpace.setIcon(QtGui.QIcon(str(Util.ICON_DIR / 'IconWIP.png')))
        self.btn_switchToSpace.clicked.connect(self.switchToSpaceClicked)

        self.btn_matchAndSwitchSpaceToControl: QtWidgets.QPushButton = self.widget.findChild(QtWidgets.QPushButton, 'btn_matchAndSwitchSpaceToControl')
        self.btn_matchAndSwitchSpaceToControl.setIcon(QtGui.QIcon(str(Util.ICON_DIR / 'IconWIP.png')))
        self.btn_matchAndSwitchSpaceToControl.clicked.connect(self.matchAndSwitchSpaceToControlClicked)

        self.btn_matchSpaceToControl: QtWidgets.QPushButton = self.widget.findChild(QtWidgets.QPushButton, 'btn_matchSpaceToControl')
        self.btn_matchSpaceToControl.setIcon(QtGui.QIcon(str(Util.ICON_DIR / 'IconWIP.png')))
        self.btn_matchSpaceToControl.clicked.connect(self.matchSpaceToControlClicked)

        self.btn_matchSpaceToSpace: QtWidgets.QPushButton = self.widget.findChild(QtWidgets.QPushButton, 'btn_matchSpaceToSpace')
        self.btn_matchSpaceToSpace.setIcon(QtGui.QIcon(str(Util.ICON_DIR / 'IconWIP.png')))
        self.btn_matchSpaceToSpace.clicked.connect(self.matchSpaceToSpaceClicked)

        self.btn_matchAndSwitchControlToSpace: QtWidgets.QPushButton = self.widget.findChild(QtWidgets.QPushButton, 'btn_matchAndSwitchControlToSpace')
        self.btn_matchAndSwitchControlToSpace.setIcon(QtGui.QIcon(str(Util.ICON_DIR / 'IconWIP.png')))
        self.btn_matchAndSwitchControlToSpace.clicked.connect(self.matchAndSwitchControlToSpaceClicked)

        self.btn_matchControlToSpace: QtWidgets.QPushButton = self.widget.findChild(QtWidgets.QPushButton, 'btn_matchControlToSpace')
        self.btn_matchControlToSpace.setIcon(QtGui.QIcon(str(Util.ICON_DIR / 'IconWIP.png')))
        self.btn_matchControlToSpace.clicked.connect(self.matchControlToSpaceClicked)

        self.btn_selectSpaceObject: QtWidgets.QPushButton = self.widget.findChild(QtWidgets.QPushButton, 'btn_selectSpaceObject')
        self.btn_selectSpaceObject.setIcon(QtGui.QIcon(str(Util.ICON_DIR / 'IconWIP.png')))
        self.btn_selectSpaceObject.clicked.connect(self.selectSpaceObjectClicked)

        self.btn_zeroSpaceObject: QtWidgets.QPushButton = self.widget.findChild(QtWidgets.QPushButton, 'btn_zeroSpaceObject')
        self.btn_zeroSpaceObject.setIcon(QtGui.QIcon(str(Util.ICON_DIR / 'IconWIP.png')))
        self.btn_zeroSpaceObject.clicked.connect(self.zeroSpaceObject)

    def switchToSpaceClicked(self):
        self.space.switchToSpace(keyEnabled=self.parentManager.cb_keyEnabled.isEnabled(),
                                 forceKeyIfAlreadyAtValue=self.parentManager.cb_forceKeyIfAlreadyAtValueEnabled.isEnabled())

    def matchAndSwitchSpaceToControlClicked(self):
        self.space.switchToSpace(keyEnabled=self.parentManager.cb_keyEnabled.isEnabled(),
                                 forceKeyIfAlreadyAtValue=self.parentManager.cb_forceKeyIfAlreadyAtValueEnabled.isEnabled())
        pass

    def matchSpaceToControlClicked(self):
        pass

    def matchSpaceToSpaceClicked(self):
        pass

    def matchAndSwitchControlToSpaceClicked(self):
        self.space.switchToSpace(keyEnabled=self.parentManager.cb_keyEnabled.isEnabled(),
                                 forceKeyIfAlreadyAtValue=self.parentManager.cb_forceKeyIfAlreadyAtValueEnabled.isEnabled())
        pass

    def matchControlToSpaceClicked(self):
        pass

    def selectSpaceObjectClicked(self):
        pass

    def zeroSpaceObject(self):
        pass

class ILLMayaSpaceSwitcherManager(QtWidgets.QWidget):
    SETTINGS = QtCore.QSettings("ILL", "MayaSpaceSwitcherManager")
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
        self.spacesIntersection: ILLMayaSpaceSwitcherModel.SpacesIntersection() = None
        self.spaceWidgetWrappers: list[IllMayaSpaceWidgetWrapper] = None

        self.setWindowFlags(QtCore.Qt.Window)
        self.widget = QtUiTools.QUiLoader().load(Util.PACKAGE_DIR / 'ILLMayaSpaceSwitcherManager.ui')
        self.widget.setParent(self)

        # Refresh Button
        self.btn_refresh: QtWidgets.QPushButton = self.widget.findChild(QtWidgets.QPushButton, 'btn_refresh')
        self.btn_refresh.clicked.connect(self.refreshPressed)

        # Selected Control Label
        self.lbl_selectedControlsList: QtWidgets.QLabel = self.widget.findChild(QtWidgets.QLabel, 'lbl_selectedControlsList')

        # Key Enabled Check Box
        self.cb_keyEnabled: QtWidgets.QCheckBox = self.widget.findChild(QtWidgets.QCheckBox, 'cb_keyEnabled')

        # Force Key if Already At Value Check Box
        self.cb_forceKeyIfAlreadyAtValueEnabled: QtWidgets.QCheckBox = self.widget.findChild(QtWidgets.QCheckBox, 'cb_forceKeyIfAlreadyAtValueEnabled')

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

        # go through each control and build the intersection of spaces
        self.spacesIntersection = ILLMayaSpaceSwitcherModel.SpacesIntersection()
        for spaces in [ILLMayaSpaceSwitcherModel.Spaces.fromControl(selectedControl) for selectedControl in self.selectedControls]:
            # early out optimization, where if we run into a space that's None, we know there is no intersection of spaces on any selections
            if spaces is None:
                return

            self.spacesIntersection.addSpaces(spaces)

        self.spacesIntersection.evaluateSpaces()

        self.spaceWidgetWrappers = []

        self.setupSpacesUI(spacesIntersectionGroup=self.spacesIntersection.spacesIntersectionGroup, groupName="Spaces")
        self.setupSpacesUI(spacesIntersectionGroup=self.spacesIntersection.rotationSpacesIntersectionGroup, groupName="Rotation Spaces")

    def setupSpacesUI(self, spacesIntersectionGroup: ILLMayaSpaceSwitcherModel.SpacesIntersectionGroup, groupName: str):
        # update the spaces UI
        if spacesIntersectionGroup is not None:
            if spacesIntersectionGroup.spaces is not None and len(spacesIntersectionGroup.spaces) > 0:
                self.sa_spacesListContents.layout().addWidget(createGroupNameWidget(groupName))

                for space in spacesIntersectionGroup.spaces:
                    spaceWidgetWrapper = IllMayaSpaceWidgetWrapper(parentManager=self, space=space)
                    self.sa_spacesListContents.layout().addWidget(spaceWidgetWrapper.widget)
                    self.spaceWidgetWrappers.append(spaceWidgetWrapper)
