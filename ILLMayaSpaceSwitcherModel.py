import json
import maya.cmds as cmds

import Util

# A definition of an individual space
class Space:
    def __init__(self,
                 name: str = '',
                 attributeName: str = '',
                 transformName: str = ''):
        # Name of the space itself, usually the attribute nice name
        self.name: str = name

        # Internal name of the attribute, the non-nice name
        self.attributeName: str = attributeName

        # The reference to the transform object in the scene
        self.transformName: str = transformName

    @classmethod
    def fromJsonData(cls, controlName: str, attributeName: str, jsonData: {}):
        if not Util.isLongName(controlName):
            raise NameError(f'Use long names only for control name "{controlName}"')

        if not cmds.attributeQuery(attributeName, node=controlName, exists=True):
            raise AttributeError(f'No attribute "{attributeName}" on control "{controlName}"')

        transformName = jsonData["transformName"]

        if not cmds.objExists(transformName):
            raise NameError(f'No object "{transformName}" exists in the scene')

        if not cmds.nodeType(transformName) == "transform":
            raise TypeError(f'Object "{transformName}" is not a transform type')

        if not Util.isLongName(transformName):
            raise NameError(f'Use long names only for transform "{transformName}"')

        return cls(name=cmds.attributeQuery(attributeName, node=controlName, niceName=True),
                   attributeName=attributeName,
                   transformName=jsonData["transformName"])

# A space group represents the list of spaces that can be switched between
# Usually you have a normal spaces group and a rotation spaces group
class SpaceGroup:
    def __init__(self,
                 name: str = '',
                 spaces: list[Space] = ()):
        # Name of the space group
        self.name: str = name

        # The spaces themselves
        self.spaces: list[Space] = spaces

    @classmethod
    def fromJsonData(cls, controlName: str, name: str, jsonData: {}):
        if not Util.isLongName(controlName):
            raise NameError(f'Use long names only for control name "{controlName}"')

        return cls(name=name,
                   spaces=[Space.fromJsonData(controlName=controlName, attributeName=attributeName, jsonData=spaceJsonData)
                           for attributeName, spaceJsonData in jsonData.items()])

# Represents the definition of a single control's collection of spaces
class Spaces:
    def __init__(self,
                 controlName: str,
                 spaceGroups: list[SpaceGroup] = ()):
        # The control name the spaces are on
        self.controlName: str = controlName

        # The space groups in this spaces collection
        self.spaceGroups: list[SpaceGroup] = spaceGroups

    @classmethod
    def fromJsonStr(cls, controlName: str, jsonStr: str):
        return cls.fromJsonData(controlName=controlName, jsonData = json.loads(jsonStr))

    @classmethod
    def fromJsonData(cls, controlName: str, jsonData: {}):
        if not Util.isLongName(controlName):
            raise NameError(f'Use long names only for control name "{controlName}"')

        return cls(controlName=controlName,
                   spaceGroups=[SpaceGroup.fromJsonData(controlName=controlName, name=groupName, jsonData=groupJsonData)
                                for groupName, groupJsonData in jsonData.items()])



# When working with multiple selected controls, this tracks the merged version where two objects have the same order of spaces within the groups
class MergedSpaces:
    def __init__(self):
        self.spaces: set[Spaces] = set()

    def addSpaces(self, spaces:Spaces) -> bool:
        spacesNum = len(self.spaces)
        self.spaces.add(spaces)

        if spacesNum == len(self.spaces):
            return False

        # TODO: Reevaluate the merged spaces

        return True

    def removeSpaces(self, spaces:Spaces) -> bool:
        spacesNum = len(self.spaces)
        self.spaces.remove(spaces)

        if spacesNum == len(self.spaces):
            return False

        # TODO: Reevaluate the merged spaces

        return True