import json
import maya.cmds as cmds

import Util

ILLMayaSpaceSwitcherConfigAttributeName: str = 'ILLMayaSpaceSwitcherConfig'

# A definition of an individual space
class Space:
    def __init__(self,
                 name: str = None,
                 attributeName: str = None,
                 transformName: str = None):
        # Name of the space itself, usually the attribute nice name
        self.name: str = name

        # Internal name of the attribute, the non-nice name
        self.attributeName: str = attributeName

        # The reference to the transform object in the scene
        self.transformName: str = transformName

    @classmethod
    def baseFromJsonData(cls, controlName: str, baseSpaceName: str, jsonData: {}):
        if not Util.isLongName(controlName):
            raise NameError(f'Use long names only for control name "{controlName}"')

        return cls(name=baseSpaceName,
                   transformName=cls.getTransformNameFromJsonData(jsonData=jsonData))

    @classmethod
    def fromJsonData(cls, controlName: str, attributeName: str, jsonData: {}):
        if not Util.isLongName(controlName):
            raise NameError(f'Use long names only for control name "{controlName}"')

        if not cmds.attributeQuery(attributeName, node=controlName, exists=True):
            raise AttributeError(f'No attribute "{attributeName}" on control "{controlName}"')

        return cls(name=cmds.attributeQuery(attributeName, node=controlName, niceName=True),
                   attributeName=attributeName,
                   transformName=cls.getTransformNameFromJsonData(jsonData=jsonData))

    @staticmethod
    def getTransformNameFromJsonData(jsonData: {}):
        transformName = jsonData['transformName']

        if not cmds.objExists(transformName):
            raise NameError(f'No object "{transformName}" exists in the scene')

        if not cmds.nodeType(transformName) == 'transform':
            raise TypeError(f'Object "{transformName}" is not a transform type')

        if not Util.isLongName(transformName):
            raise NameError(f'Use long names only for transform "{transformName}"')

# A space group represents the list of spaces that can be switched between
# Usually you have a normal spaces group and a rotation spaces group
class SpaceGroup:
    def __init__(self,
                 name: str = None,
                 spaces: list[Space] = None):
        # Name of the space group
        self.name: str = name

        # The spaces themselves
        self.spaces: list[Space] = spaces

    @classmethod
    def fromJsonData(cls, controlName: str, name: str, jsonData: {}):
        if not Util.isLongName(controlName):
            raise NameError(f'Use long names only for control name "{controlName}"')

        # We expect a bool field named hasBaseSpace to determine if the first space is a base space

        return cls(name=name,
                   spaces=[Space.baseFromJsonData(controlName=controlName, baseSpaceName=attributeOrBaseSpaceName, jsonData=spaceJsonData)
                           if index == 0 else
                           Space.fromJsonData(controlName=controlName, attributeName=attributeOrBaseSpaceName, jsonData=spaceJsonData)
                           for index, (attributeOrBaseSpaceName, spaceJsonData) in enumerate(jsonData.items())])

# Represents the definition of a single control's collection of spaces
class Spaces:
    def __init__(self,
                 controlName: str = None,
                 spaces: SpaceGroup = None,
                 rotationSpaces: SpaceGroup = None):
        # The control name the spaces are on
        self.controlName: str = controlName

        # The main spaces
        self.spaces: SpaceGroup = spaces

        # The rotation only spaces
        self.rotationSpaces: SpaceGroup = rotationSpaces

    @classmethod
    def fromJsonStr(cls, controlName: str, jsonStr: str):
        return cls.fromJsonData(controlName=controlName, jsonData = json.loads(jsonStr))

    @classmethod
    def fromJsonData(cls, controlName: str, jsonData: {}):
        if not Util.isLongName(controlName):
            raise NameError(f'Use long names only for control name "{controlName}"')

        spacesJsonData = jsonData.get("Spaces", None)
        rotationSpacesJsonData = jsonData.get("Rotation Spaces", None)

        return cls(controlName=controlName,
                   spaces=SpaceGroup.fromJsonData(controlName=controlName, name="Spaces", jsonData=spacesJsonData) if spacesJsonData is not None else None,
                   rotationSpaces=SpaceGroup.fromJsonData(controlName=controlName, name="Rotation Spaces", jsonData=rotationSpacesJsonData) if rotationSpacesJsonData is not None else None)

class SpacesUnionListEntry:
    def __init__(self):
        self.spaces: list[Space] = None

# When working with multiple selected controls, this tracks the union of what the selected spaces are among the objects as long as their space names match and are in the same order
class SpacesUnion:
    def __init__(self):
        self.spaces: set[Spaces] = set()

    def addSpaces(self, spaces:Spaces) -> bool:
        spacesNum = len(self.spaces)
        self.spaces.add(spaces)

        if spacesNum == len(self.spaces):
            return False

        return True

    def removeSpaces(self, spaces:Spaces) -> bool:
        spacesNum = len(self.spaces)
        self.spaces.remove(spaces)

        if spacesNum == len(self.spaces):
            return False

        return True

    def evaluateSpaces(self):
        pass