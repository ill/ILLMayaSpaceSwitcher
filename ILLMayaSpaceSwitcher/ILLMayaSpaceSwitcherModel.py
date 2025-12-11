import json
import maya.cmds as cmds
import maya.api.OpenMaya as om
import math

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
        return self.parentSpaceGroup.getControlName()

    def getSpaceIndex(self) -> int:
        return self.parentSpaceGroup.getSpaceIndex(self)

    def isRotationSpace(self) -> bool:
        return self.parentSpaceGroup.isRotationSpace()

    def hasSpaces(self) -> bool:
        return self.parentSpaceGroup.hasSpaces()

    def hasRotationSpaces(self) -> bool:
        return self.parentSpaceGroup.hasRotationSpaces()

    def getTransformWorldTransform(self):
        return om.MMatrix(cmds.getAttr(f'{self.transformName}.worldMatrix'))

    def getTransformInverseWorldTransform(self):
        return om.MMatrix(cmds.getAttr(f'{self.transformName}.worldInverseMatrix'))

    def getTransformParentInverseWorldTransform(self):
        return om.MMatrix(cmds.getAttr(f'{self.transformName}.parentInverseMatrix'))

    def getControlWorldTransform(self):
        return self.parentSpaceGroup.getControlWorldTransform()

    def getControlLocalTransform(self):
        return self.parentSpaceGroup.getControlLocalTransform()

    def getControlInverseLocalTransform(self):
        return self.parentSpaceGroup.getControlInverseLocalTransform()

    def getControlParentInverseWorldTransform(self):
        return self.parentSpaceGroup.getControlParentInverseWorldTransform()

    def getControlRotationSpaceLocalRotation(self):
        return self.parentSpaceGroup.getControlRotationSpaceLocalRotation()

    def getControlRotationSpaceInverseLocalRotation(self):
        return self.parentSpaceGroup.getControlRotationSpaceInverseLocalRotation()

    def getControlRotationSpaceLocalRotationTransform(self):
        return self.parentSpaceGroup.getControlRotationSpaceLocalRotationTransform()

    # Switches to this space
    def switchToSpace(self, keyEnabled:bool = False, forceKeyIfAlreadyAtValue:bool = False):
        # Set the attribute of every control after us to 0
        for spaceIndex in range(self.getSpaceIndex() + 1, len(self.parentSpaceGroup.spaces)):
            self.parentSpaceGroup.spaces[spaceIndex].setAttribute(attributeValue=0, keyEnabled=keyEnabled, forceKeyIfAlreadyAtValue=forceKeyIfAlreadyAtValue)

        self.setAttribute(attributeValue=1, keyEnabled=keyEnabled, forceKeyIfAlreadyAtValue=forceKeyIfAlreadyAtValue)

    def matchToControl(self, keyEnabled: bool = False):
        if self.transformName is not None:
            # TODO: For rotation space, the joint orient should be the same in the end
            # Find what the joint orient would be if we were to switch to this space
            # Counter rotate by that amount?

            if self.isRotationSpace():
                # Find what the joint orient of the rotation space would end up being when set to this space and counter rotate the transform by that
                # This is the rotation space joint orient now
                preMoveControlRotationSpaceLocalRotationTransform = self.getControlRotationSpaceLocalRotationTransform()

            # Find control relative transform, put us at the inverse of that
            controlWorldTransform = self.getControlWorldTransform()
            inverseLocalTransform = self.getControlInverseLocalTransform()

            destinationWorldTransform = inverseLocalTransform * controlWorldTransform
            destinationLocalTransform = destinationWorldTransform * self.getTransformParentInverseWorldTransform()

            cmds.xform(self.transformName, matrix=list(destinationLocalTransform))

            if self.isRotationSpace():
                tempAttributeStates = self.parentSpaceGroup.getAttributes()

                # Force a temporary switch to space to force things to be at the new transform for a bit so our computations work for getting what would be the joint orient
                self.switchToSpace()

                # counter rotate rotation on the transform to account for the change in joint orient
                postMoveControlRotationSpaceLocalRotationTransform = self.getControlRotationSpaceLocalRotationTransform()

                # Restore it back to normal now, in case we're not actually switching to this space after
                self.parentSpaceGroup.setAttributes(tempAttributeStates)

                # Counter rotate by the delta in the joint orient
                destinationToCurrentRelativeTransform = preMoveControlRotationSpaceLocalRotationTransform * postMoveControlRotationSpaceLocalRotationTransform.inverse()

                thing = controlWorldTransform * destinationWorldTransform.inverse()

                pre = Util.getOmTransformRotation(preMoveControlRotationSpaceLocalRotationTransform)
                post = Util.getOmTransformRotation(postMoveControlRotationSpaceLocalRotationTransform)

                print(pre)
                print(post)

                rotationSpaceLocalTransformCounterRotate = Util.getOmTransformRotation(destinationToCurrentRelativeTransform)
                thing = Util.getOmTransformRotation(thing)

                print(thing)

                # cmds.rotate(rotationSpaceLocalTransformCounterRotate[0] - thing[0],
                #             rotationSpaceLocalTransformCounterRotate[1] - thing[1],
                #             rotationSpaceLocalTransformCounterRotate[2] - thing[2],
                #             self.transformName,
                #             relative=True)

                cmds.rotate(thing[0],
                            thing[1],
                            thing[2],
                            self.transformName,
                            relative=True)

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
        # The base rotation space should be allowed to have this called on it by pulling from the base space transform
        if self.transformName is not None or (self.isRotationSpace() and self.getSpaceIndex() == 0):
            if self.hasRotationSpaces():
                # Find what the joint orient of the rotation space would end up being when set to this space and counter rotate the transform by that
                # This is the rotation space joint orient now
                currentControlRotationSpaceLocalRotationTransform = self.getControlRotationSpaceLocalRotationTransform()

            if self.isRotationSpace():
                # This is the rotation space joint orient that it would be if we switched to this space
                # If we're switching to the base rotation space there's no transform name, so the destination rotation space will be nothing
                destinationControlRotationSpaceLocalTransform = self.getTransformWorldTransform() * self.getControlParentInverseWorldTransform() if self.transformName else om.MMatrix.kIdentity
            else:
                # This is the local transform of the control that it would be if we switched to this space
                destinationControlLocalTransform = self.getControlWorldTransform() * self.getTransformInverseWorldTransform()

                # Set the control to the new transform
                cmds.xform(self.getControlName(), matrix=list(destinationControlLocalTransform))

                if self.hasRotationSpaces():
                    tempAttributeStates = self.parentSpaceGroup.getAttributes()

                    # Force a temporary switch to space to force things to be at the new transform for a bit so our computations work for getting what would be the joint orient
                    self.switchToSpace()

                    destinationControlRotationSpaceLocalTransform = self.getControlRotationSpaceLocalRotationTransform()

                    # Restore it back to normal now, in case we're not actually switching to this space after
                    self.parentSpaceGroup.setAttributes(tempAttributeStates)

            if self.hasRotationSpaces():
                # Counter rotate by the delta in the joint orient
                destinationToCurrentRelativeTransform = currentControlRotationSpaceLocalRotationTransform * destinationControlRotationSpaceLocalTransform.inverse()

                rotationSpaceLocalTransformCounterRotate = Util.getOmTransformRotation(destinationToCurrentRelativeTransform)

                cmds.rotate(rotationSpaceLocalTransformCounterRotate[0],
                            rotationSpaceLocalTransformCounterRotate[1],
                            rotationSpaceLocalTransformCounterRotate[2],
                            self.getControlName(),
                            relative=True)

            if keyEnabled:
                if self.isRotationSpace():
                    Util.keyRotation(self.getControlName())
                else:
                    Util.keyTransforms(self.getControlName())

    def getAttribute(self) -> float:
        if self.attributeName is None:
            return 0.0

        return cmds.getAttr(f'{self.getControlName()}.{self.attributeName}')


    def setAttribute(self, attributeValue: float, keyEnabled: bool = False, forceKeyIfAlreadyAtValue: bool = False):
        if self.attributeName is not None:
            controlName = self.getControlName()

            if forceKeyIfAlreadyAtValue or self.getAttribute() != attributeValue:
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

    def getControlName(self) -> str:
        return self.parentSpaces.controlName

    def getSpaceIndex(self, space: Space) -> int:
        return self.spaces.index(space)

    def isRotationSpace(self) -> bool:
        return self == self.parentSpaces.rotationSpaces

    def hasSpaces(self) -> bool:
        return self.parentSpaces.hasSpaces()

    def hasRotationSpaces(self) -> bool:
        return self.parentSpaces.hasRotationSpaces()

    def getControlWorldTransform(self):
        return self.parentSpaces.getControlWorldTransform()

    def getControlLocalTransform(self):
        return self.parentSpaces.getControlLocalTransform()

    def getControlInverseLocalTransform(self):
        return self.parentSpaces.getControlInverseLocalTransform()

    def getControlParentInverseWorldTransform(self):
        return self.parentSpaces.getControlParentInverseWorldTransform()

    def getControlRotationSpaceLocalRotation(self):
        return self.parentSpaces.getControlRotationSpaceLocalRotation()

    def getControlRotationSpaceInverseLocalRotation(self):
        return self.parentSpaces.getControlRotationSpaceInverseLocalRotation()

    def getControlRotationSpaceLocalRotationTransform(self):
        return self.parentSpaces.getControlRotationSpaceLocalRotationTransform()

    # Gets the current state of all the attributes in the space group now
    def getAttributes(self) -> list[float]:
        return [space.getAttribute() for space in self.spaces]

    # Restores the state of all the attributes in the space group to these values
    def setAttributes(self, attributes:list[float]) :
        for index, attribute in enumerate(attributes):
            self.spaces[index].setAttribute(attribute)


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

    def hasSpaces(self) -> bool:
        return self.spaces is not None

    def hasRotationSpaces(self) -> bool:
        return self.rotationSpaces is not None

    def getControlWorldTransform(self):
        if self.controlName is None:
            raise NameError(f'No control name on space.')

        return om.MMatrix(cmds.getAttr(f'{self.controlName}.worldMatrix'))

    def getControlLocalTransform(self):
        if self.controlName is None:
            raise NameError(f'No control name on space.')

        return om.MMatrix(cmds.getAttr(f'{self.controlName}.matrix'))

    def getControlInverseLocalTransform(self):
        if self.controlName is None:
            raise NameError(f'No control name on space.')

        return om.MMatrix(cmds.getAttr(f'{self.controlName}.inverseMatrix'))

    def getControlParentWorldTransform(self):
        if self.controlName is None:
            raise NameError(f'No control name on space.')

        return om.MMatrix(cmds.getAttr(f'{self.controlName}.parentMatrix'))

    def getControlParentInverseWorldTransform(self):
        if self.controlName is None:
            raise NameError(f'No control name on space.')

        return om.MMatrix(cmds.getAttr(f'{self.controlName}.parentInverseMatrix'))

    def getControlRotationSpaceLocalRotation(self):
        if not self.hasRotationSpaces():
            return 0.0, 0.0, 0.0

        return cmds.getAttr(f'{self.controlName}.jointOrient')[0]

    def getControlRotationSpaceInverseLocalRotation(self):
        if self.controlName is None:
            raise NameError(f'No control name on space.')

        jointOrient = self.getControlRotationSpaceLocalRotation()

        return -jointOrient[0], -jointOrient[1], -jointOrient[2]

    def getControlRotationSpaceLocalRotationTransform(self):
        if self.controlName is None:
            raise NameError(f'No control name on space.')

        controlRotationSpaceLocalRotation = self.getControlRotationSpaceLocalRotation()

        return om.MEulerRotation(math.radians(controlRotationSpaceLocalRotation[0]),
                                 math.radians(controlRotationSpaceLocalRotation[1]),
                                 math.radians(controlRotationSpaceLocalRotation[2]),
                                 Util.getOmRotationOrder(self.controlName)).asMatrix()

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

