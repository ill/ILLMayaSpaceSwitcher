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
        self.parentSpaceGroup = None

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

    # Switches to this space
    def switchToSpace(self, keyEnabled:bool = False, forceKeyIfAlreadyAtValue:bool = False):
        # Find the control we belong to
        controlName = self.parentSpaceGroup.parentSpaces.controlName

        # Find which index in the space group we belong to
        ourSpaceIndex = self.parentSpaceGroup.spaces.index(self)

        # Set the attribute of every control after us to 0
        for spaceIndex in range(ourSpaceIndex + 1, len(self.parentSpaceGroup.spaces)):
            space:Space = self.parentSpaceGroup.spaces[spaceIndex]

            spaceAttributeName = space.attributeName

            if spaceAttributeName is None:
                raise AttributeError(f'Only the first space in the group is allowed to have no attribute, meaning it\'s a base space. Space index "{spaceIndex}" has no attribute name.')

            if forceKeyIfAlreadyAtValue or cmds.getAttr(f'{controlName}.{spaceAttributeName}') != 0:
                cmds.setAttr(f'{controlName}.{spaceAttributeName}', 0)

                if keyEnabled:
                    cmds.setKeyframe(controlName, attribute=spaceAttributeName)

        # Set our attribute value to 1 if we aren't a base space and have an attribute
        if self.attributeName is not None:
            if forceKeyIfAlreadyAtValue or cmds.getAttr(f'{controlName}.{self.attributeName}') != 1:
                cmds.setAttr(f'{controlName}.{self.attributeName}', 1)

                if keyEnabled:
                    cmds.setKeyframe(controlName, attribute=self.attributeName)

# A space group represents the list of spaces that can be switched between
# Usually you have a normal spaces group and a rotation spaces group
class SpaceGroup:
    def __init__(self,
                 name: str = None,
                 spaces: list[Space] = None):
        self.parentSpaces = None

        # Name of the space group
        self.name: str = name

        # The spaces themselves
        self.spaces: list[Space] = spaces

        # Some setup an extra validation
        for spaceIndex, space in enumerate(self.spaces):
            # only the first space is allowed to not have an attribute name, meaning it's a base space
            if spaceIndex == 0 and space.attributeName is None:
                raise AttributeError(f'Only the first space in the group is allowed to have no attribute, meaning it\'s a base space. Space index "{spaceIndex}" has no attribute name.')

            space.parentSpaceGroup = self

    @classmethod
    def fromJsonData(cls, parentSpaces, controlName: str, name: str, jsonData: {}):
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
        self.spaces.parentSpaces = self

        # The rotation only spaces
        self.rotationSpaces: SpaceGroup = rotationSpaces
        self.rotationSpaces.parentSpaces = self

    @staticmethod
    def getJsonStrFromControl(controlName: str) -> str:
        if (controlName is not None
                and cmds.attributeQuery(ILLMayaSpaceSwitcherConfigAttributeName,
                                        node=controlName,
                                        exists=True)
                and cmds.getAttr(f'{controlName}.{ILLMayaSpaceSwitcherConfigAttributeName}',
                                 type=True) == 'string'):
            return cmds.getAttr(f'{controlName}.{ILLMayaSpaceSwitcherConfigAttributeName}')
        else:
            return None

    @classmethod
    def fromControl(cls, controlName: str):
        jsonStr = cls.getJsonStrFromControl(controlName=controlName)
        return cls.fromJsonStr(controlName=controlName, jsonStr=jsonStr) if jsonStr is not None else None

    @classmethod
    def fromJsonStr(cls, controlName: str, jsonStr: str):
        return cls.fromJsonData(controlName=controlName, jsonData = json.loads(jsonStr)) if jsonStr is not None else None

    @classmethod
    def fromJsonData(cls, controlName: str, jsonData: {}):
        if not Util.isLongName(controlName):
            raise NameError(f'Use long names only for control name "{controlName}"')

        spacesJsonData = jsonData.get('Spaces', None)
        rotationSpacesJsonData = jsonData.get('Rotation Spaces', None)

        return cls(controlName=controlName,
                   spaces=SpaceGroup.fromJsonData(controlName=controlName, name='Spaces', jsonData=spacesJsonData) if spacesJsonData is not None else None,
                   rotationSpaces=SpaceGroup.fromJsonData(controlName=controlName, name='Rotation Spaces', jsonData=rotationSpacesJsonData) if rotationSpacesJsonData is not None else None)

class SpacesIntersectionSpace:
    def __init__(self, name: str = '', spaces:list[Space] = None):
        self.name = name
        self.spaces = spaces

class SpacesIntersectionGroup:
    def __init__(self, name: str = ''):
        self.name = name
        self.spaces: list[SpacesIntersectionSpace] = None

    def evaluateGroups(self, spaceGroups:list[SpaceGroup]):
        self.spaces = None

        if spaceGroups is None or len(spaceGroups) <= 0:
            return

        # First create an array from the very first selected group of space names
        self.spaces = [SpacesIntersectionSpace(space.name, [space]) for space in spaceGroups[0].spaces]

        # Now go through every subsequent space and check to see if the names are in the same orders of the space names sets so far
        for groupIndex in range(1, len(spaceGroups)):
            spaceGroup = spaceGroups[groupIndex]

            orderedSpaceNamesIndex = 0
            spaceIndex = 0

            while orderedSpaceNamesIndex < len(self.spaces):
                # if we reached the end of the other space group then erase the rest of the list
                if spaceIndex >= len(spaceGroup.spaces):
                    del self.spaces[orderedSpaceNamesIndex:]
                    break

                didFind = False

                # look for the space name in spaceIntersectionSpaces, if there, then we're good on this named space, otherwise remove it from the intersection so far
                while spaceIndex < len(spaceGroup.spaces):
                    if self.spaces[orderedSpaceNamesIndex].name == spaceGroup.spaces[spaceIndex].name:
                        self.spaces[orderedSpaceNamesIndex].spaces.append(spaceGroup.spaces[spaceIndex])
                        orderedSpaceNamesIndex += 1
                        spaceIndex += 1
                        didFind = True
                        break
                    else:
                        spaceIndex += 1

                if not didFind:
                    del self.spaces[orderedSpaceNamesIndex]

# When working with multiple selected controls, this tracks the intersection of the set of what the selected spaces are among the objects as long as their space names match and are in the same order
class SpacesIntersection:
    def __init__(self):
        self.spaces: set[Spaces] = set()

        self.spacesIntersectionGroup: SpacesIntersectionGroup = None
        self.rotationSpacesIntersectionGroup: SpacesIntersectionGroup = None

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
            # If we encounter a None space, we definitely have no intersection of anything
            if space is None:
                return

            if space.spaces is None:
                allSpacesHaveSpaces = False

            if space.rotationSpaces is None:
                allSpacesHaveRotationSpaces = False

        if allSpacesHaveSpaces:
            self.spacesIntersectionGroup = SpacesIntersectionGroup("Spaces")
            self.spacesIntersectionGroup.evaluateGroups([space.spaces for space in self.spaces])
        else:
            self.spacesIntersectionGroup = None

        if allSpacesHaveRotationSpaces:
            self.rotationSpacesIntersectionGroup = SpacesIntersectionGroup("Rotation Spaces")
            self.rotationSpacesIntersectionGroup.evaluateGroups([space.rotationSpaces for space in self.spaces])
        else:
            self.rotationSpacesIntersectionGroup = None
