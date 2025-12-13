# Add this to a shelf button to open the main UI
# import ILLMayaSpaceSwitcherConfiguration
# ILLMayaSpaceSwitcherConfiguration.ILLMayaSpaceSwitcherConfiguration.openMayaMainToolWindowInstance()

import maya.cmds as cmds
from maya import OpenMayaUI as omui
# TODO: Figure out maya < 2025 and >= 2025 support
# from shiboken2 import wrapInstance
# from PySide2 import QtUiTools, QtCore, QtGui, QtWidgets
from shiboken6 import wrapInstance
from PySide6 import QtUiTools, QtCore, QtWidgets
import pathlib

from . import Util
from . import ILLMayaSpaceSwitcherModel


class ILLMayaSpaceSwitcherConfiguration(QtWidgets.QWidget):
    SETTINGS = QtCore.QSettings("ILL", "MayaSpaceSwitcherConfiguration")
    GEOMETRY_SETTING = "geometry"
    SPLITTER_SETTING = "splitter"

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
        self.widget = QtUiTools.QUiLoader().load(Util.PACKAGE_DIR / 'ILLMayaSpaceSwitcherConfiguration.ui')
        self.widget.setParent(self)

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

        # Validate JSON Button
        self.btn_validate: QtWidgets.QPushButton = self.widget.findChild(QtWidgets.QPushButton, 'btn_validate')
        self.btn_validate.clicked.connect(self.validatePressed)

        # Set Space Configuration on Control Button
        self.btn_set: QtWidgets.QPushButton = self.widget.findChild(QtWidgets.QPushButton, 'btn_set')
        self.btn_set.clicked.connect(self.setPressed)

        # Get Selected Object Name Button
        self.btn_getSelectedObjectName: QtWidgets.QPushButton = self.widget.findChild(QtWidgets.QPushButton, 'btn_getSelectedObjectName')
        self.btn_getSelectedObjectName.clicked.connect(self.getSelectedObjectNamePressed)

        # Selection Name Line Edit
        self.le_selectionName: QtWidgets.QLineEdit = self.widget.findChild(QtWidgets.QLineEdit, 'le_selectionName')

        # Splitter
        self.splitter: QtWidgets.QSplitter = self.widget.findChild(QtWidgets.QSplitter, 'splitter')

        # Get Selected Control Attributes Button
        self.btn_getSelectedControlAttributes: QtWidgets.QPushButton = self.widget.findChild(QtWidgets.QPushButton, 'btn_getSelectedControlAttributes')
        self.btn_getSelectedControlAttributes.clicked.connect(self.getSelectedControlAttributesPressed)

        # Selected Control Attributes Editor
        self.te_selectedControlAttributes: QtWidgets.QPlainTextEdit = self.widget.findChild(QtWidgets.QPlainTextEdit, 'te_selectedControlAttributes')

        # set initial window geometry
        restoredGeometry = ILLMayaSpaceSwitcherConfiguration.SETTINGS.value(
            ILLMayaSpaceSwitcherConfiguration.GEOMETRY_SETTING, None)

        if restoredGeometry is None:
            self.resize(800, 480)
        else:
            try:
                self.restoreGeometry(restoredGeometry)
            except Exception:
                self.resize(800, 480)

        restoredSplitter = ILLMayaSpaceSwitcherConfiguration.SETTINGS.value(
            ILLMayaSpaceSwitcherConfiguration.SPLITTER_SETTING, None)

        if restoredSplitter is not None:
            try:
                self.splitter.restoreState(restoredSplitter)
            except Exception:
                pass

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

        ILLMayaSpaceSwitcherConfiguration.SETTINGS.setValue(ILLMayaSpaceSwitcherConfiguration.GEOMETRY_SETTING, self.saveGeometry())
        ILLMayaSpaceSwitcherConfiguration.SETTINGS.setValue(ILLMayaSpaceSwitcherConfiguration.SPLITTER_SETTING, self.splitter.saveState())

        super().closeEvent(event)

    def refreshPressed(self):
        self.setSelectedControl(Util.getSelectedTransform())

    def generateDefaultJsonContentsPressed(self):
        self.te_jsonContents.setPlainText(
            '{\n'
            '\t"Spaces": {\n'
            '\t\t"Definitions": [\n'
            '\t\t\t{\n'
            '\t\t\t\t"name": "Space World (Can be omitted and derived from attribute nice name, required if no attribute name)",\n'
            '\t\t\t\t"attributeName": "InternalAttributeName (Not Nice Name but internal script name, omit for first base space if no attribute associated with space)",\n'
            '\t\t\t\t"transformName": "|LongName|COG_CTRL__space_world__LOC"\n'
            '\t\t\t},\n'
            '\t\t\t{\n'
            '\t\t\t\t"attributeName": "InternalAttributeName (Not Nice Name but internal script name)",\n'
            '\t\t\t\t"transformName": "|LongName|COG_CTRL__space_rig_main__LOC"\n'
            '\t\t\t}\n'
            '\t\t]\n'
            '\t},\n'
            '\t"Rotation Spaces": {\n'
            '\t\t"Definitions": [\n'
            '\t\t\t{\n'
            '\t\t\t\t"name": "Space World (Can be omitted and derived from attribute nice name, required if no attribute name)",\n'
            '\t\t\t\t"attributeName": "InternalAttributeName (Not Nice Name but internal script name, omit for first base space if no attribute associated with space)",\n'
            '\t\t\t\t"transformName": "|LongName|COG_CTRL_rot__space_world__LOC"\n'
            '\t\t\t},\n'
            '\t\t\t{\n'
            '\t\t\t\t"attributeName": "InternalAttributeName 2 (Not Nice Name but internal script name)",\n'
            '\t\t\t\t"transformName": "|LongName|COG_CTRL_rot__space_rig_main__LOC"\n'
            '\t\t\t}\n'
            '\t\t]\n'
            '\t}\n'
            '}'
        )

    def validate(self):
        if self.selectedControl is None:
            QtWidgets.QMessageBox.warning(self, 'Error', 'Select a rig control and press refresh.')
            return False

        try:
            ILLMayaSpaceSwitcherModel.Spaces.fromJsonStr(self.selectedControl, self.te_jsonContents.toPlainText())
        except Exception as e:
            QtWidgets.QMessageBox.warning(self, 'Error', f'Validation failed: {type(e).__name__}\n\n{e}')
            return False

        return True

    def validatePressed(self):
        if self.validate():
            QtWidgets.QMessageBox.information(self, 'Success', 'Validation succeeded')

    def setPressed(self):
        if self.validate():
            cmds.undoInfo(openChunk=True, chunkName='ILL Maya Space Switcher Configuration')

            try:
                if not cmds.attributeQuery(ILLMayaSpaceSwitcherModel.ILLMayaSpaceSwitcherConfigAttributeName,
                                           node=self.selectedControl,
                                           exists=True):
                    cmds.addAttr(self.selectedControl,
                                 longName=ILLMayaSpaceSwitcherModel.ILLMayaSpaceSwitcherConfigAttributeName,
                                 dataType='string',
                                 hidden=False)
                    cmds.setAttr(f'{self.selectedControl}.{ILLMayaSpaceSwitcherModel.ILLMayaSpaceSwitcherConfigAttributeName}',
                                 e=True,
                                 channelBox=False)
                elif not cmds.getAttr(f'{self.selectedControl}.{ILLMayaSpaceSwitcherModel.ILLMayaSpaceSwitcherConfigAttributeName}', type=True) == 'string':
                    QtWidgets.QMessageBox.warning(self, 'Error', f'Attribute "{ILLMayaSpaceSwitcherModel.ILLMayaSpaceSwitcherConfigAttributeName}" on "{self.selectedControl}" exists but is not of string type. Delete it to proceed.')
                    return

                cmds.setAttr(f'{self.selectedControl}.{ILLMayaSpaceSwitcherModel.ILLMayaSpaceSwitcherConfigAttributeName}',
                             self.te_jsonContents.toPlainText(),
                             type='string')

                QtWidgets.QMessageBox.information(self, 'Success', 'Validation succeeded and set the Control_Configuration attribute')
            finally:
                cmds.undoInfo(closeChunk=True)

    def getSelectedObjectNamePressed(self):
        self.le_selectionName.setText(Util.getSelectedTransform())

    def getSelectedControlAttributesPressed(self):
        if self.selectedControl is None:
            self.te_selectedControlAttributes.setPlainText(None)
        else:
            attrs = cmds.listAttr(self.selectedControl, keyable=True)
            attrsString: str = ''

            for attr in attrs:
                attrsString += attr + '\n'

            self.te_selectedControlAttributes.setPlainText(attrsString)

    def setSelectedControl(self, selectedControl:str):
        if self.selectedControl == selectedControl:
            return

        self.selectedControl = selectedControl

        self.lbl_selectedControl.setText(f'Selected Control: {Util.getShortName(self.selectedControl)}')

        self.te_jsonContents.setPlainText(ILLMayaSpaceSwitcherModel.Spaces.getJsonStrFromControl(self.selectedControl))
