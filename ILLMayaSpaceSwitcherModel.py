import json
import maya.cmds as cmds

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
    def fromJsonData(cls, control: str, attributeName: str, jsonData: {}):
        if not cmds.attributeQuery(attributeName, node=control, exists=True):
            raise ValueError(f'No attribute: {attributeName} on control: {control}')

        return Space(name=cmds.attributeQuery(attributeName, node=control, niceName=True),
                     attributeName=attributeName,
                     transformName=jsonData["transformName"])

# A space group represents the list of spaces that can be switched between
# Usually you have a normal spaces group and a rotation spaces group
class SpaceGroup:
    def __init__(self,
                 name: str = '',
                 spaces: list[Space] = ()):
        self.name = name
        self.spaces: list[Space] = spaces

    @classmethod
    def fromJsonData(cls, control: str, name: str, jsonData: {}):
        return cls(name=name, spaces=[Space.fromJsonData(control=control, attributeName=attributeName, jsonData=spaceJsonData)
                                      for attributeName, spaceJsonData in jsonData.items()])

# Represents the definition of a single control's collection of spaces
class Spaces:
    def __init__(self,
                 spaceGroups: list[SpaceGroup] = ()):
        self.spaceGroups: list[SpaceGroup] = spaceGroups

    @classmethod
    def fromJsonStr(cls, control: str, jsonStr: str):
        return cls.fromJsonData(control=control, jsonData = json.loads(jsonStr))

    @classmethod
    def fromJsonData(cls, control: str, jsonData: {}):
        return cls(spaceGroups=[SpaceGroup.fromJsonData(control=control, name=groupName, jsonData=groupJsonData)
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