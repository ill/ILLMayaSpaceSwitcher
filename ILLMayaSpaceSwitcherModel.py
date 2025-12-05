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
    def fromJsonData(cls, controlName: str, jsonData: {}):
        if not Util.isLongName(controlName):
            raise NameError(f'Use long names only for control name "{controlName}"')

        name = jsonData.get('name', None)
        attributeName = jsonData.get('attributeName', None)

        if name is None:
            if attributeName is None:
                raise NameError(f'attributeName and name are both unspecified for space definition')

            name = cmds.attributeQuery(attributeName, node=controlName, niceName=True)

        transformName = jsonData.get('transformName', None)

        if transformName is not None:
            if not cmds.objExists(transformName):
                raise NameError(f'No object "{transformName}" exists in the scene')

            if not cmds.nodeType(transformName) == 'transform':
                raise TypeError(f'Object "{transformName}" is not a transform type')

            if not Util.isLongName(transformName):
                raise NameError(f'Use long names only for transform "{transformName}"')

        if attributeName is not None and not cmds.attributeQuery(attributeName, node=controlName, exists=True):
            raise AttributeError(f'No attribute "{attributeName}" on control "{controlName}"')

        return cls(name=name,
                   attributeName=attributeName,
                   transformName=transformName)

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

        definitionsJsonData = jsonData.get('Definitions', None)

        return cls(name=name,
                   spaces=[Space.fromJsonData(controlName=controlName, jsonData=spaceDefinitionJsonData)
                           for spaceDefinitionJsonData in definitionsJsonData] if definitionsJsonData is not None else None)

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

        spacesJsonData = jsonData.get('Spaces', None)
        rotationSpacesJsonData = jsonData.get('Rotation Spaces', None)

        return cls(controlName=controlName,
                   spaces=SpaceGroup.fromJsonData(controlName=controlName, name='Spaces', jsonData=spacesJsonData) if spacesJsonData is not None else None,
                   rotationSpaces=SpaceGroup.fromJsonData(controlName=controlName, name='Rotation Spaces', jsonData=rotationSpacesJsonData) if rotationSpacesJsonData is not None else None)

class SpacesUnionSpace:
    def __init__(self, name: str = '', spaces:list[Space] = None):
        self.name = name
        self.spaces = spaces

class SpacesUnionGroup:
    def __init__(self, name: str = ''):
        self.name = name
        self.spaces: list[SpacesUnionSpace] = None

    def evaluateGroups(self, spaceGroups:list[SpaceGroup]):
        self.spaces = None

        if spaceGroups is None or len(spaceGroups) <= 0:
            return

        # First create an array from the very first selected group of space names
        spaceUnionSpaces = [SpacesUnionSpace(space.name, [space]) for space in spaceGroups[0].spaces]

        # Now go through every subsequent space and check to see if the names are in the same orders of the space names sets so far
        for groupIndex in range(1, len(spaceGroups)):
            spaceGroup = spaceGroups[groupIndex]

            orderedSpaceNamesIndex = 0
            spaceIndex = 0

            while orderedSpaceNamesIndex < len(spaceUnionSpaces) and spaceIndex < len(spaceGroup.spaces):
                didFind = False

                # look for the space name in orderedSpaceNamesIndex, if there, then we're good on this name
                while spaceIndex < len(spaceGroup.spaces):
                    if spaceUnionSpaces[orderedSpaceNamesIndex].name == spaceGroup.spaces[spaceIndex].name:
                        spaceUnionSpaces[orderedSpaceNamesIndex].spaces.append(spaceGroup.spaces[spaceIndex])
                        orderedSpaceNamesIndex += 1
                        spaceIndex += 1
                        didFind = True
                        break
                    else:
                        spaceIndex += 1

                if not didFind:
                    del spaceUnionSpaces[orderedSpaceNamesIndex]

# When working with multiple selected controls, this tracks the union of what the selected spaces are among the objects as long as their space names match and are in the same order
class SpacesUnion:
    def __init__(self):
        self.spaces: set[Spaces] = set()

        self.spacesUnionGroup: SpacesUnionGroup = None
        self.rotationSpacesUnionGroup: SpacesUnionGroup = None

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
        # Check if all spaces have spaces and rot spaces
        allSpacesHaveSpaces = True
        allSpacesHaveRotationSpaces = True

        for space in self.spaces:
            if space.spaces is None:
                allSpacesHaveSpaces = False

            if space.rotationSpaces is None:
                allSpacesHaveRotationSpaces = False

        if allSpacesHaveSpaces:
            self.spacesUnionGroup = SpacesUnionGroup("Spaces")
            self.spacesUnionGroup.evaluateGroups([space.spaces for space in self.spaces])
        else:
            self.spacesUnionGroup = None

        if allSpacesHaveRotationSpaces:
            self.rotationSpacesUnionGroup = SpacesUnionGroup("Rotation Spaces")
            self.rotationSpacesUnionGroup.evaluateGroups([space.rotationSpaces for space in self.spaces])
        else:
            self.rotationSpacesUnionGroup = None
