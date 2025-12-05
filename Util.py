import maya.cmds as cmds

def getSelectedTransforms():
    return cmds.ls(sl=True, type='transform', long=True)

def getSelectedTransform():
    selectedTransforms = getSelectedTransforms()
    return getSelectedTransforms()[0] if len(selectedTransforms) > 0 else None

def getShortName(longName):
    return cmds.ls(longName, sn=True)[0] if longName is not None else None

def isLongName(name: str) -> bool:
    return ("|" in name) if name is not None else False
