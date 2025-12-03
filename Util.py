import maya.cmds as cmds
import maya.mel as mel

def getSelectedTransforms():
    return cmds.ls(sl=True, dag=True, type='transform', long=True)

def getSelectedTransform():
    return getSelectedTransforms()[0]

def getShortName(longName):
    return cmds.ls(longName, sn=True)[0]