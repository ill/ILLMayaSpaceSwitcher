import json
import maya.cmds as cmds
import maya.api.OpenMaya as om

from . import Util

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

    def getControlName(self) -> str:
        return self.parentSpaceGroup.parentSpaces.controlName

    def getSpaceIndex(self) -> int:
        return self.parentSpaceGroup.spaces.index(self)

    def isRotationSpace(self) -> bool:
        return self.parentSpaceGroup == self.parentSpaceGroup.parentSpaces.rotationSpaces

    def hasRotationSpace(self) -> bool:
        return self.parentSpaceGroup.parentSpaces.rotationSpaces is not None

    def getTransformWorldTransform(self):
        return om.MMatrix(cmds.getAttr(f'{self.transformName}.worldMatrix'))

    def getTransformInverseWorldTransform(self):
        return om.MMatrix(cmds.getAttr(f'{self.transformName}.worldInverseMatrix'))

    def getTransformParentInverseWorldTransform(self):
        return om.MMatrix(cmds.getAttr(f'{self.transformName}.parentInverseMatrix'))

    def getControlWorldTransform(self):
        return om.MMatrix(cmds.getAttr(f'{self.getControlName()}.worldMatrix'))

    def getControlLocalTransform(self):
        return om.MMatrix(cmds.getAttr(f'{self.getControlName()}.matrix'))

    def getControlInverseLocalTransform(self):
        return om.MMatrix(cmds.getAttr(f'{self.getControlName()}.inverseMatrix'))

    def getControlParentInverseWorldTransform(self):
        return om.MMatrix(cmds.getAttr(f'{self.getControlName()}.parentInverseMatrix'))

    def getControlRotationSpaceLocalRotation(self):
        if not self.hasRotationSpace():
            return 0.0, 0.0, 0.0

        return cmds.getAttr(f'{self.getControlName()}.jointOrient')

    def getControlRotationSpaceInverseLocalRotation(self):
        jointOrient = self.getControlLocalRotation()

        return -jointOrient[0], -jointOrient[1], -jointOrient[2]

    # Switches to this space
    def switchToSpace(self, keyEnabled:bool = False, forceKeyIfAlreadyAtValue:bool = False):
        # Set the attribute of every control after us to 0
        for spaceIndex in range(self.getSpaceIndex() + 1, len(self.parentSpaceGroup.spaces)):
            self.parentSpaceGroup.spaces[spaceIndex].setAttribute(attributeValue=0, keyEnabled=keyEnabled, forceKeyIfAlreadyAtValue=forceKeyIfAlreadyAtValue)

        self.setAttribute(attributeValue=1, keyEnabled=keyEnabled, forceKeyIfAlreadyAtValue=forceKeyIfAlreadyAtValue)

    def matchToControl(self, keyEnabled: bool = False):
        if self.transformName is not None:
            # Find control relative transform, put us at the inverse of that
            if self.isRotationSpace():
                # TODO: Implement
                pass
            else:
                # TODO: if has rotation space, account for the joint orient? Seems to work actually

                controlWorldTransform = self.getControlWorldTransform()
                inverseLocalTransform = self.getControlInverseLocalTransform()

                destinationWorldTransform = inverseLocalTransform * controlWorldTransform
                destinationLocalTransform = destinationWorldTransform * self.getTransformParentInverseWorldTransform()

                cmds.xform(self.transformName, matrix=list(destinationLocalTransform))

                if keyEnabled:
                    Util.keyTransforms(self.transformName)

    def matchToSpace(self, spaceToMatch, keyEnabled: bool = False):
        # Find transform of control relative to space object
        # Set our transform to be the inverse of that

        if self.transformName is not None and spaceToMatch.transformName is not None:
            if self.isRotationSpace():
                # TODO: Implement
                pass
            else:
                # TODO: if has rotation space, account for the joint orient? Seems to work actually

                destinationWorldTransform = spaceToMatch.getTransformWorldTransform()
                destinationLocalTransform = destinationWorldTransform * self.getTransformParentInverseWorldTransform()

                cmds.xform(self.transformName, matrix=list(destinationLocalTransform))

                if keyEnabled:
                    Util.keyTransforms(self.transformName)

    def matchControlToSpace(self, keyEnabled: bool = False):
        if self.transformName is not None:
            if self.isRotationSpace():
                # Find what the joint orient of the rotation space would end up being when set to this space and counter rotate the transform by that

                controlRotationSpaceInverseLocalRotation = self.getControlRotationSpaceInverseLocalRotation()

                rotationSpaceLocalTransform = self.getTransformWorldTransform() * self.getControlParentInverseWorldTransform()

                rotationSpaceLocalRotationRadians = om.MTransformationMatrix(rotationSpaceLocalTransform).rotation()
                rotationSpaceLocalRotation = (om.MAngle(rotationSpaceLocalRotationRadians.x).asDegrees(),
                                              om.MAngle(rotationSpaceLocalRotationRadians.y).asDegrees(),
                                              om.MAngle(rotationSpaceLocalRotationRadians.z).asDegrees())

                cmds.rotate(controlRotationSpaceInverseLocalRotation[0]-rotationSpaceLocalRotation[0],
                            controlRotationSpaceInverseLocalRotation[1]-rotationSpaceLocalRotation[1],
                            controlRotationSpaceInverseLocalRotation[2]-rotationSpaceLocalRotation[2],
                            self.getControlName(),
                            relative=True)

                if keyEnabled:
                    Util.keyRotation(self.getControlName())

            else:
                # Find relative transform between control and the space, set control transform to that relative transform

                controlRotationSpaceInverseLocalRotation = self.getControlRotationSpaceInverseLocalRotation()

                controlWorldTransform = self.getControlWorldTransform()
                transformInverseWorldTransform = self.getTransformInverseWorldTransform()

                destinationControlLocalTransform = controlWorldTransform * transformInverseWorldTransform

                # Set the control to the new transform
                cmds.xform(self.getControlName(), matrix=list(destinationControlLocalTransform))

                # Counter rotate to account for the rotation space
                cmds.rotate(controlRotationSpaceInverseLocalRotation[0],
                            controlRotationSpaceInverseLocalRotation[1],
                            controlRotationSpaceInverseLocalRotation[2],
                            self.getControlName(),
                            relative=True)

                if keyEnabled:
                    Util.keyTransforms(self.getControlName())

    def setAttribute(self, attributeValue: float, keyEnabled: bool = False, forceKeyIfAlreadyAtValue: bool = False):
        if self.attributeName is not None:
            controlName = self.getControlName()

            if forceKeyIfAlreadyAtValue or cmds.getAttr(f'{controlName}.{self.attributeName}') != attributeValue:
                cmds.setAttr(f'{controlName}.{self.attributeName}', attributeValue)

                if keyEnabled:
                    cmds.setKeyframe(controlName, attribute=self.attributeName)

    def selectTransform(self):
        if self.transformName is not None:
            cmds.select(self.transformName, add=True)

    def zeroTransform(self):
        if self.transformName is not None:
            cmds.setAttr(f'{self.transformName}.translateX', 0)
            cmds.setAttr(f'{self.transformName}.translateY', 0)
            cmds.setAttr(f'{self.transformName}.translateZ', 0)

            cmds.setAttr(f'{self.transformName}.rotateX', 0)
            cmds.setAttr(f'{self.transformName}.rotateY', 0)
            cmds.setAttr(f'{self.transformName}.rotateZ', 0)

            cmds.setAttr(f'{self.transformName}.scaleX', 1)
            cmds.setAttr(f'{self.transformName}.scaleY', 1)
            cmds.setAttr(f'{self.transformName}.scaleZ', 1)

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
            if spaceIndex != 0 and space.attributeName is None:
                raise AttributeError(f'Only the first space in the group is allowed to have no attribute, meaning it\'s a base space. Space index "{spaceIndex}" has no attribute name.')

            space.parentSpaceGroup = self

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
        if self.spaces is not None:
            self.spaces.parentSpaces = self

        # The rotation only spaces
        self.rotationSpaces: SpaceGroup = rotationSpaces
        if self.rotationSpaces is not None:
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

        # Rotation spaces should only exist on controls that are "joints"
        if not cmds.nodeType(controlName) == 'joint':
            raise TypeError(f'Rotation spaces should only exist on joint type controls because it uses the joint orient to control the rotation space')

        return cls(controlName=controlName,
                   spaces=SpaceGroup.fromJsonData(controlName=controlName, name='Spaces', jsonData=spacesJsonData) if spacesJsonData is not None else None,
                   rotationSpaces=SpaceGroup.fromJsonData(controlName=controlName, name='Rotation Spaces', jsonData=rotationSpacesJsonData) if rotationSpacesJsonData is not None else None)

class SpacesIntersectionSpace:
    def __init__(self, parentSpacesIntersectionGroup, name: str = '', spaces:list[Space] = None):
        self.parentSpacesIntersectionGroup = parentSpacesIntersectionGroup
        self.name = name
        self.spaces = spaces

    def switchToSpace(self, keyEnabled: bool = False, forceKeyIfAlreadyAtValue: bool = False):
        for space in self.spaces:
            space.switchToSpace(keyEnabled=keyEnabled, forceKeyIfAlreadyAtValue=forceKeyIfAlreadyAtValue)

    def setAttribute(self, attributeValue:float, keyEnabled: bool = False, forceKeyIfAlreadyAtValue: bool = False):
        for space in self.spaces:
            space.setAttribute(attributeValue=attributeValue, keyEnabled=keyEnabled, forceKeyIfAlreadyAtValue=forceKeyIfAlreadyAtValue)

    def matchToControl(self, keyEnabled: bool = False):
        for space in self.spaces:
            space.matchToControl(keyEnabled=keyEnabled)

    def matchToSpace(self, spacesIntersectionToMatch, keyEnabled: bool = False):
        for space in self.spaces:
            for spaceToMatch in spacesIntersectionToMatch.spaces:
                if space.parentSpaceGroup == spaceToMatch.parentSpaceGroup:
                    space.matchToSpace(spaceToMatch=spaceToMatch, keyEnabled=keyEnabled)

    def matchControlToSpace(self, keyEnabled: bool = False):
        for space in self.spaces:
            space.matchControlToSpace(keyEnabled=keyEnabled)

    def selectTransform(self):
        cmds.select(clear=True)

        for space in self.spaces:
            space.selectTransform()

    def zeroTransform(self):
        for space in self.spaces:
            space.zeroTransform()

class SpacesIntersectionGroup:
    def __init__(self, parentSpacesIntersection, name: str = ''):
        self.parentSpacesIntersection = parentSpacesIntersection
        self.name = name
        self.spaces: list[SpacesIntersectionSpace] = None

    def evaluateGroups(self, spaceGroups:list[SpaceGroup]):
        self.spaces = None

        if spaceGroups is None or len(spaceGroups) <= 0:
            return

        # First create an array from the very first selected group of space names
        self.spaces = [SpacesIntersectionSpace(parentSpacesIntersectionGroup=self, name=space.name, spaces=[space]) for space in spaceGroups[0].spaces]

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
            self.spacesIntersectionGroup = SpacesIntersectionGroup(parentSpacesIntersection=self, name="Spaces")
            self.spacesIntersectionGroup.evaluateGroups([space.spaces for space in self.spaces])
        else:
            self.spacesIntersectionGroup = None

        if allSpacesHaveRotationSpaces:
            self.rotationSpacesIntersectionGroup = SpacesIntersectionGroup(parentSpacesIntersection=self, name="Rotation Spaces")
            self.rotationSpacesIntersectionGroup.evaluateGroups([space.rotationSpaces for space in self.spaces])
        else:
            self.rotationSpacesIntersectionGroup = None

