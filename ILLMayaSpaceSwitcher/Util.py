import maya.cmds as cmds
from PySide6 import QtUiTools, QtCore, QtGui, QtWidgets

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
