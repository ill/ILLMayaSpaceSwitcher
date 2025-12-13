import maya.cmds as cmds
import maya.api.OpenMaya as om
import maya.utils
from PySide6 import QtUiTools, QtCore, QtGui, QtWidgets
import pathlib

PACKAGE_DIR = pathlib.Path(__file__).parent.resolve()
ICON_DIR = PACKAGE_DIR / "resources" / "icons"

class KeyOptions:
    def __init__(self,
                 keyEnabled: bool = False,
                 forceKeyIfAlreadyAtValue: bool = False,
                 stepTangentKeys: bool = False):
        self.keyEnabled: bool = keyEnabled
        self.forceKeyIfAlreadyAtValue: bool = forceKeyIfAlreadyAtValue
        self.stepTangentKeys: bool = stepTangentKeys

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

TRANSLATE_X = 'translateX'
TRANSLATE_Y = 'translateY'
TRANSLATE_Z = 'translateZ'

TRANSLATE_ATTRIBUTES = [TRANSLATE_X, TRANSLATE_Y, TRANSLATE_Z]

ROTATE_X = 'rotateX'
ROTATE_Y = 'rotateY'
ROTATE_Z = 'rotateZ'

ROTATE_ATTRIBUTES = [ROTATE_X, ROTATE_Y, ROTATE_Z]

SCALE_X = 'scaleX'
SCALE_Y = 'scaleY'
SCALE_Z = 'scaleZ'

SCALE_ATTRIBUTES = [SCALE_X, SCALE_Y, SCALE_Z]

TR_ATTRIBUTES = TRANSLATE_ATTRIBUTES + ROTATE_ATTRIBUTES
TRS_ATTRIBUTES = TR_ATTRIBUTES + SCALE_ATTRIBUTES

def getAttributeDictionary(node:str, attributes:list[str])->dict[str, float]:
    res = dict[str, float]()

    for attribute in attributes:
        res[attribute] = cmds.getAttr(f'{node}.{attribute}')

    return res

# Returns a dictionary of attribute name to value
def getTransformAttributeDictionary(node:str)->dict[str, float]:
    return getAttributeDictionary(node=node, attributes=TRS_ATTRIBUTES)

def keyAttribute(node:str, attribute:str, keyOptions:KeyOptions, originalValues:dict[str, float]):
    if not keyOptions.keyEnabled:
        return

    currentValue = cmds.getAttr(f'{node}.{attribute}')

    if attribute in originalValues and originalValues[attribute] == currentValue and not keyOptions.forceKeyIfAlreadyAtValue:
        return

    if keyOptions.stepTangentKeys:
        cmds.setKeyframe(node, attribute=attribute, inTangentType='step', outTangentType='step')
    else:
        cmds.setKeyframe(node, attribute=attribute)

def keyAttributes(node:str, attributes:[str], keyOptions:KeyOptions, originalValues:dict[str, float]):
    if not keyOptions.keyEnabled:
        return

    for attribute in attributes:
        keyAttribute(node=node, attribute=attribute, keyOptions=keyOptions, originalValues=originalValues)

def keyTransform(node:str, keyOptions:KeyOptions, originalValues:dict[str, float]):
    keyAttributes(node=node, attributes=TRS_ATTRIBUTES, keyOptions=keyOptions, originalValues=originalValues)

def keyRotation(node:str, keyOptions:KeyOptions, originalValues:dict[str, float]):
    keyAttributes(node=node, attributes=ROTATE_ATTRIBUTES, keyOptions=keyOptions, originalValues=originalValues)

def getOmRotationOrder(node:str):
    return [
        om.MEulerRotation.kXYZ,
        om.MEulerRotation.kYZX,
        om.MEulerRotation.kZXY,
        om.MEulerRotation.kXZY,
        om.MEulerRotation.kYXZ,
        om.MEulerRotation.kZYX,
    ][cmds.getAttr(f'{node}.rotateOrder')]

def getOmTransformRotation(matrix:om.MMatrix):
    radians = om.MTransformationMatrix(matrix).rotation()
    return (om.MAngle(radians.x).asDegrees(),
            om.MAngle(radians.y).asDegrees(),
            om.MAngle(radians.z).asDegrees())
