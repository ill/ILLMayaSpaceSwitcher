import maya.cmds as cmds

from . import Util
from . import ILLMayaSpaceSwitcherModel

class ILLMayaSpaceSwitcherAutoGenerator:
    def __init__(self, controlName: str):
        self.controlName = controlName
        self.spaceAttributes: list[str] = []
        self.rotationSpaceAttributes: list[str] = []

        self.processControl()

        self.spaces: ILLMayaSpaceSwitcherModel.Spaces = None

        try:
            self.spaces = ILLMayaSpaceSwitcherModel.Spaces(controlName=controlName,
                                                           spaces=ILLMayaSpaceSwitcherModel.SpaceGroup(name='Spaces',
                                                                                                       spaces=self.createSpaces(attributeNames=self.spaceAttributes, isRotationSpace=False)),
                                                           rotationSpaces=ILLMayaSpaceSwitcherModel.SpaceGroup(name='Rotation Spaces',
                                                                                                               spaces=self.createSpaces(attributeNames=self.rotationSpaceAttributes, isRotationSpace=True)))
        except Exception as e:
            print(e)

    def getJsonData(self) -> {}:
        return self.spaces.getJsonData() if self.spaces is not None else None

    def getJsonString(self) -> str:
        return self.spaces.getJsonString() if self.spaces is not None else None

    def processControl(self):
        if self.controlName is None:
            return None

        self.processControlAttributes()

    def processControlAttributes(self):
        if self.controlName is None:
            return None

        self.spaceAttributes = []
        self.rotationSpaceAttributes = []

        # Find attributes on the control
        for attribute in cmds.listAttr(self.controlName, userDefined=True):
            niceName = cmds.attributeQuery(attribute, node=self.controlName, niceName=True)

            # If it starts with Space it's a space
            if niceName.startswith('Space '):
                self.spaceAttributes.append(attribute)

            # If it starts with Rot Space it's a rotation space
            elif niceName.startswith('Rot Space '):
                self.rotationSpaceAttributes.append(attribute)

    def createSpaces(self, attributeNames: list[str], isRotationSpace: bool) -> list[ILLMayaSpaceSwitcherModel.Space]:
        res: list[ILLMayaSpaceSwitcherModel.Space] = []

        # Create a "Spaces" rotation space for the first rotation space to signify it's using the "Spaces" space
        if isRotationSpace and len(self.spaceAttributes) > 0 and len(attributeNames):
            res.append(ILLMayaSpaceSwitcherModel.Space(name='Spaces'))

        for attribute in attributeNames:
            res.append(self.createSpace(attributeName=attribute, isRotationSpace=isRotationSpace))

        return res

    def createSpace(self, attributeName: str, isRotationSpace: bool) -> ILLMayaSpaceSwitcherModel.Space:
        # If not keyable, the space name is the attribute nice name
        if cmds.getAttr(f'{self.controlName}.{attributeName}', keyable=True):
            return ILLMayaSpaceSwitcherModel.Space(attributeName=attributeName,
                                                   defaultAttributeValue=cmds.getAttr(f'{self.controlName}.{attributeName}'),
                                                   transformName=self.findSpaceTransform(attributeName=attributeName, isRotationSpace=isRotationSpace))
        else:
            return ILLMayaSpaceSwitcherModel.Space(name=cmds.attributeQuery(attributeName, node=self.controlName, niceName=True),
                                                   transformName=self.findSpaceTransform(attributeName=attributeName, isRotationSpace=isRotationSpace))

    def findSpaceTransform(self, attributeName: str, isRotationSpace: bool) -> str:
        spaceTransformShortName = self.getSpaceTransformShortName(attributeName=attributeName, isRotationSpace=isRotationSpace)

        foundTransforms = cmds.ls(f'*|{spaceTransformShortName}', long=True)

        attributeNiceName = cmds.attributeQuery(attributeName, node=self.controlName, niceName=True)

        print(f'findSpaceTransform\n=======\nAttribute: "{attributeName}" Nice Name: "{attributeNiceName}"')

        if len(foundTransforms) > 0:
            for foundTransform in foundTransforms:
                print(f'=======\nFound space transform {foundTransform} for short name {spaceTransformShortName}. Choosing only the first one if there are duplicates')

            return foundTransforms[0]
        else:
            print(f'No Space Transform with name {spaceTransformShortName} found')
            return f'|NOT_FOUND|{spaceTransformShortName}'

    def getSpaceTransformShortName(self, attributeName: str, isRotationSpace: bool) -> str:
        # Find an object with this name:
        # It takes the attribute nice name and turns it into lower case with underscores for where the spaces are

        controlNamePart = self.getSpaceTransformObjectNameControlNameString(isRotationSpace=isRotationSpace)
        attributeNamePart = self.getSpaceTransformObjectNameAttributeNameString(attributeName=attributeName, isRotationSpace=isRotationSpace)

        return f'{controlNamePart}_rot__{attributeNamePart}__LOC' if isRotationSpace else f'{controlNamePart}__{attributeNamePart}__LOC'

    def getSpaceTransformObjectNameControlNameString(self, isRotationSpace: bool) -> str:
        return Util.getShortName(self.controlName)

    def getSpaceTransformObjectNameAttributeNameString(self, attributeName: str, isRotationSpace: bool) -> str:
        attributeNiceName = cmds.attributeQuery(attributeName, node=self.controlName, niceName=True)

        res = attributeNiceName

        # Remove the Rot at the start for rotation spaces
        if isRotationSpace:
            res = res[len('Rot '):]

        # Some special cases
        if res == 'Space COG':
            return 'space_COG'

        if res.startswith('Space Aux '):
            auxSpaceNumber = int(attributeNiceName[len('Space Aux '):])
            return f'space_auxiliary_{auxSpaceNumber:02d}'

        return res.lower().replace(' ', '_')
