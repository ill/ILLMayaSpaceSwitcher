# Add this to a shelf button to open the main UI
# import ILLMayaSpaceSwitcherManager
# ILLMayaSpaceSwitcherManager.ILLMayaSpaceSwitcherManager.openMayaMainToolWindowInstance()

import maya.cmds as cmds
from maya import OpenMayaUI as omui
# TODO: Figure out maya < 2025 and >= 2025 support
# from shiboken2 import wrapInstance
# from PySide2 import QtUiTools, QtCore, QtGui, QtWidgets
from shiboken6 import wrapInstance
from PySide6 import QtUiTools, QtCore, QtGui, QtWidgets
import pathlib

from . import Util
from . import ILLMayaSpaceSwitcherModel


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

        # Switch to Space Button
        self.btn_switchToSpace: QtWidgets.QPushButton = self.widget.findChild(QtWidgets.QPushButton, 'btn_switchToSpace')
        self.btn_switchToSpace.setIcon(QtGui.QIcon(str(Util.ICON_DIR / 'EnableAndSwitchToSpace.png')))
        self.btn_switchToSpace.clicked.connect(self.switchToSpaceClicked)

        # Enable Space Button
        self.btn_enableSpace: QtWidgets.QPushButton = self.widget.findChild(QtWidgets.QPushButton, 'btn_enableSpace')
        self.btn_enableSpace.setIcon(QtGui.QIcon(str(Util.ICON_DIR / 'EnableSpace.png')))
        self.btn_enableSpace.clicked.connect(self.enableSpaceClicked)

        # Disable Space Button
        self.btn_disableSpace: QtWidgets.QPushButton = self.widget.findChild(QtWidgets.QPushButton, 'btn_disableSpace')
        self.btn_disableSpace.setIcon(QtGui.QIcon(str(Util.ICON_DIR / 'DisableSpace.png')))
        self.btn_disableSpace.clicked.connect(self.disableSpaceClicked)

        # Match and Switch Space to Control Button
        self.btn_matchAndSwitchSpaceToControl: QtWidgets.QPushButton = self.widget.findChild(QtWidgets.QPushButton, 'btn_matchAndSwitchSpaceToControl')
        self.btn_matchAndSwitchSpaceToControl.setIcon(QtGui.QIcon(str(Util.ICON_DIR / 'MatchAndSwitchSpaceToControl.png')))
        self.btn_matchAndSwitchSpaceToControl.clicked.connect(self.matchAndSwitchSpaceToControlClicked)

        # Match Space to Control Button
        self.btn_matchSpaceToControl: QtWidgets.QPushButton = self.widget.findChild(QtWidgets.QPushButton, 'btn_matchSpaceToControl')
        self.btn_matchSpaceToControl.setIcon(QtGui.QIcon(str(Util.ICON_DIR / 'MatchSpaceToControl.png')))
        self.btn_matchSpaceToControl.clicked.connect(self.matchSpaceToControlClicked)

        # Match Space to Space Button
        self.btn_matchSpaceToSpace: QtWidgets.QPushButton = self.widget.findChild(QtWidgets.QPushButton, 'btn_matchSpaceToSpace')
        self.btn_matchSpaceToSpace.setIcon(QtGui.QIcon(str(Util.ICON_DIR / 'MatchSpaceToSpace.png')))
        self.btn_matchSpaceToSpace.clicked.connect(self.matchSpaceToSpaceClicked)

        # Match and Switch Control to Space Button
        self.btn_matchAndSwitchControlToSpace: QtWidgets.QPushButton = self.widget.findChild(QtWidgets.QPushButton, 'btn_matchAndSwitchControlToSpace')
        self.btn_matchAndSwitchControlToSpace.setIcon(QtGui.QIcon(str(Util.ICON_DIR / 'MatchControlToSpaceAndSwitch.png')))
        self.btn_matchAndSwitchControlToSpace.clicked.connect(self.matchAndSwitchControlToSpaceClicked)

        # Match control to Space Button
        self.btn_matchControlToSpace: QtWidgets.QPushButton = self.widget.findChild(QtWidgets.QPushButton, 'btn_matchControlToSpace')
        self.btn_matchControlToSpace.setIcon(QtGui.QIcon(str(Util.ICON_DIR / 'MatchControlToSpace.png')))
        self.btn_matchControlToSpace.clicked.connect(self.matchControlToSpaceClicked)

        # Select Space Object Button
        self.btn_selectSpaceObject: QtWidgets.QPushButton = self.widget.findChild(QtWidgets.QPushButton, 'btn_selectSpaceObject')
        self.btn_selectSpaceObject.setIcon(QtGui.QIcon(str(Util.ICON_DIR / 'SelectSpaceObject.png')))
        self.btn_selectSpaceObject.clicked.connect(self.selectSpaceObjectClicked)

        # Zero Space Object Button
        self.btn_zeroSpaceObject: QtWidgets.QPushButton = self.widget.findChild(QtWidgets.QPushButton, 'btn_zeroSpaceObject')
        self.btn_zeroSpaceObject.setIcon(QtGui.QIcon(str(Util.ICON_DIR / 'ZeroSpaceObject.png')))
        self.btn_zeroSpaceObject.clicked.connect(self.zeroSpaceObject)

    def getKeyOptions(self) -> Util.KeyOptions:
        return self.parentManager.getKeyOptions()

    def switchToSpaceClicked(self):
        def operation(keyOptions:Util.KeyOptions):
            self.space.switchToSpace(keyOptions=keyOptions)

        Util.performOperation(operation, undoChunkName='ILL Maya Space Switcher Switch to Space', keyOptions=self.getKeyOptions())

    def enableSpaceClicked(self):
        def operation(keyOptions:Util.KeyOptions):
            self.space.setAttribute(attributeValue=1, keyOptions=keyOptions)

        Util.performOperation(operation, undoChunkName='ILL Maya Space Switcher Enable Space', keyOptions=self.getKeyOptions())

    def disableSpaceClicked(self):
        def operation(keyOptions:Util.KeyOptions):
            self.space.setAttribute(attributeValue=0, keyOptions=keyOptions)

        Util.performOperation(operation, undoChunkName='ILL Maya Space Switcher Disable Space', keyOptions=self.getKeyOptions())

    def matchAndSwitchSpaceToControlClicked(self):
        def operation(keyOptions:Util.KeyOptions):
            self.space.matchToControl(keyOptions=keyOptions)
            self.space.switchToSpace(keyOptions=keyOptions)

        Util.performOperation(operation, undoChunkName='ILL Maya Space Switcher Match and Switch Space to Control', keyOptions=self.getKeyOptions())

    def matchSpaceToControlClicked(self):
        def operation(keyOptions:Util.KeyOptions):
            self.space.matchToControl(keyOptions=keyOptions)

        Util.performOperation(operation, undoChunkName='ILL Maya Space Switcher Match Space to Control', keyOptions=self.getKeyOptions())

    def matchSpaceToSpaceClicked(self):
        # Show popup menu of spaces excluding ours
        menu = QtWidgets.QMenu(self.widget)

        for space in self.space.parentSpacesIntersectionGroup.spaces:
            if space != self.space:
                action = menu.addAction(space.name)
                action.setData(space)

        chosenSpace = menu.exec(self.btn_matchSpaceToSpace.mapToGlobal(self.btn_matchSpaceToSpace.rect().bottomLeft()))

        if chosenSpace is not None:
            def operation(keyOptions: Util.KeyOptions):
                self.space.matchToSpace(spacesIntersectionToMatch=chosenSpace.data(), keyOptions=keyOptions)

            Util.performOperation(operation, undoChunkName='ILL Maya Space Switcher Match Space to Space', keyOptions=self.getKeyOptions())

    def matchAndSwitchControlToSpaceClicked(self):
        def operation(keyOptions:Util.KeyOptions):
            self.space.matchControlToSpace(keyOptions=keyOptions)
            self.space.switchToSpace(keyOptions=keyOptions)

        Util.performOperation(operation, undoChunkName='ILL Maya Space Switcher Match and Switch Control to Space', keyOptions=self.getKeyOptions())

    def matchControlToSpaceClicked(self):
        def operation(keyOptions:Util.KeyOptions):
            self.space.matchControlToSpace(keyOptions=keyOptions)

        Util.performOperation(operation, undoChunkName='ILL Maya Space Switcher Match Control to Space', keyOptions=self.getKeyOptions())

    def selectSpaceObjectClicked(self):
        def operation(keyOptions:Util.KeyOptions):
            self.space.selectTransform()

        Util.performOperation(operation, undoChunkName='ILL Maya Space Switcher Select Space Object', keyOptions=self.getKeyOptions())

    def zeroSpaceObject(self):
        def operation(keyOptions:Util.KeyOptions):
            self.space.zeroTransform(keyOptions=keyOptions)

        Util.performOperation(operation, undoChunkName='ILL Maya Space Switcher Zero Space Object', keyOptions=self.getKeyOptions())


class ILLMayaSpaceSwitcherManager(QtWidgets.QWidget):
    SETTINGS = QtCore.QSettings("ILL", "MayaSpaceSwitcherManager")
    GEOMETRY_SETTING = "geometry"
    KEY_ENABLED_SETTING = 'key_enabled'
    FORCE_KEY_IF_ALREADY_AT_VALUE_ENABLED_SETTING = 'force_key_if_already_at_value_enabled'
    STEP_TANGENT_KEYS_ENABLED_SETTING = 'step_tangent_keys_enabled'

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

        # Step Tangent Keys Enabled Check Box
        self.cb_stepTangentKeysEnabled: QtWidgets.QCheckBox = self.widget.findChild(QtWidgets.QCheckBox, 'cb_stepTangentKeysEnabled')

        # Restore Default Space Attribute Values Button
        self.btn_restoreDefaultAttributes: QtWidgets.QPushButton = self.widget.findChild(QtWidgets.QPushButton, 'btn_restoreDefaultAttributes')
        self.btn_restoreDefaultAttributes.clicked.connect(self.restoreDefaultAttributesPressed)

        # Restore Default Space Attribute Values and Match Control Button
        self.btn_restoreAndMatchDefaultAttributes: QtWidgets.QPushButton = self.widget.findChild(QtWidgets.QPushButton, 'btn_restoreAndMatchDefaultAttributes')
        self.btn_restoreAndMatchDefaultAttributes.clicked.connect(self.restoreAndMatchDefaultAttributesPressed)

        # Spaces List Contents
        self.sa_spacesListContents: QtWidgets.QWidget = self.widget.findChild(QtWidgets.QWidget, 'sa_spacesListContents')

        # set initial window geometry
        restoredGeometry = ILLMayaSpaceSwitcherManager.SETTINGS.value(ILLMayaSpaceSwitcherManager.GEOMETRY_SETTING, None)

        if restoredGeometry is None:
            self.resize(800, 480)
        else:
            try:
                self.restoreGeometry(restoredGeometry)
            except Exception:
                print("Failed to restore geometry setting")
                self.resize(800, 480)

        try:
            self.cb_keyEnabled.setChecked(ILLMayaSpaceSwitcherManager.SETTINGS.value(ILLMayaSpaceSwitcherManager.KEY_ENABLED_SETTING, self.cb_keyEnabled.isChecked(), type=bool))
        except Exception:
            print("Failed to restore keyEnabled setting")

        try:
            self.cb_forceKeyIfAlreadyAtValueEnabled.setChecked(ILLMayaSpaceSwitcherManager.SETTINGS.value(ILLMayaSpaceSwitcherManager.FORCE_KEY_IF_ALREADY_AT_VALUE_ENABLED_SETTING, self.cb_forceKeyIfAlreadyAtValueEnabled.isChecked(), type=bool))
        except Exception:
            print("Failed to restore forceKeyIfAlreadyAtValueEnabled setting")

        try:
            self.cb_stepTangentKeysEnabled.setChecked(ILLMayaSpaceSwitcherManager.SETTINGS.value(ILLMayaSpaceSwitcherManager.STEP_TANGENT_KEYS_ENABLED_SETTING, self.cb_stepTangentKeysEnabled.isChecked(), type=bool))
        except Exception:
            print("Failed to restore stepTangentKeysEnabled setting")

    def getKeyOptions(self) -> Util.KeyOptions:
        return Util.KeyOptions(keyEnabled=self.cb_keyEnabled.isChecked(),
                               forceKeyIfAlreadyAtValue=self.cb_forceKeyIfAlreadyAtValueEnabled.isChecked(),
                               stepTangentKeys=self.cb_stepTangentKeysEnabled.isChecked())

    def resizeEvent(self, event):
        """
        Called on automatically generated resize event
        """
        super().resizeEvent(event)

        self.widget.resize(self.width(), self.height())

    def closeEvent(self, event):
        """
        Close window.
        """

        ILLMayaSpaceSwitcherManager.SETTINGS.setValue(ILLMayaSpaceSwitcherManager.GEOMETRY_SETTING, self.saveGeometry())

        ILLMayaSpaceSwitcherManager.SETTINGS.setValue(ILLMayaSpaceSwitcherManager.KEY_ENABLED_SETTING, self.cb_keyEnabled.isChecked())
        ILLMayaSpaceSwitcherManager.SETTINGS.setValue(ILLMayaSpaceSwitcherManager.FORCE_KEY_IF_ALREADY_AT_VALUE_ENABLED_SETTING, self.cb_forceKeyIfAlreadyAtValueEnabled.isChecked())
        ILLMayaSpaceSwitcherManager.SETTINGS.setValue(ILLMayaSpaceSwitcherManager.STEP_TANGENT_KEYS_ENABLED_SETTING, self.cb_stepTangentKeysEnabled.isChecked())

        print(type(ILLMayaSpaceSwitcherManager.SETTINGS.value(ILLMayaSpaceSwitcherManager.FORCE_KEY_IF_ALREADY_AT_VALUE_ENABLED_SETTING, self.cb_forceKeyIfAlreadyAtValueEnabled.isChecked())).__name__)

        super().closeEvent(event)

    def refreshPressed(self):
        self.setSelectedControls(selectedControls=Util.getSelectedTransforms())

    def restoreDefaultAttributesPressed(self):
        if self.spacesIntersection is not None:
            def operation(keyOptions: Util.KeyOptions):
                self.spacesIntersection.restoreDefaultAttributes(keyOptions=self.getKeyOptions())

            Util.performOperation(operation, undoChunkName='ILL Maya Space Switcher Restore Default Attributes', keyOptions=self.getKeyOptions())

    def restoreAndMatchDefaultAttributesPressed(self):
        pass

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
