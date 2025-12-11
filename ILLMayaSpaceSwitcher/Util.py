import maya.cmds as cmds
import maya.api.OpenMaya as om
import maya.utils
from PySide6 import QtUiTools, QtCore, QtGui, QtWidgets
import pathlib

PACKAGE_DIR = pathlib.Path(__file__).parent.resolve()
ICON_DIR = PACKAGE_DIR / "resources" / "icons"

def getSelectedTransforms():
    return cmds.ls(sl=True, type='transform', long=True)

def getSelectedTransform():
    selectedTransforms = getSelectedTransforms()
    return getSelectedTransforms()[0] if len(selectedTransforms) > 0 else None

def getShortName(longName):
    return cmds.ls(longName, sn=True)[0] if longName is not None else None

def isLongName(name: str) -> bool:
    return ("|" in name) if name is not None else False

def clearWidget(widget: QtWidgets.QWidget):
    if widget is None:
        return

    if widget.layout() is not None:
        clearLayout(widget.layout())
    else:
        for subWidget in widget.findChildren(QtWidgets.QWidget):
            subWidget.setParent(None)
            subWidget.deleteLater()

def clearLayout(layout: QtWidgets.QLayout):
    if layout is None:
        return

    while layout.count():
        item = layout.takeAt(0)

        widget = item.widget()
        if widget is not None:
            widget.setParent(None)
            widget.deleteLater()

def keyTransforms(node:str):
    cmds.setKeyframe(node, attribute=['translateX', 'translateY', 'translateZ',
                                      'rotateX', 'rotateY', 'rotateZ',
                                      'scaleX', 'scaleY', 'scaleZ'])

def keyRotation(node:str):
    cmds.setKeyframe(node, attribute=['rotateX', 'rotateY', 'rotateZ'])

def getOmRotationOrder(node:str):
    return [
        om.MEulerRotation.kXYZ,
        om.MEulerRotation.kYZX,
        om.MEulerRotation.kZXY,
        om.MEulerRotation.kXZY,
        om.MEulerRotation.kYXZ,
        om.MEulerRotation.kZYX,
    ][cmds.getAttr(f'{node}.rotateOrder')]
