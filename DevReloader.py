import ILLMayaSpaceSwitcher.Util
import ILLMayaSpaceSwitcher.ILLMayaSpaceSwitcherModel
import ILLMayaSpaceSwitcher.ILLMayaSpaceSwitcherAutoGenerator
import ILLMayaSpaceSwitcher.ILLMayaSpaceSwitcherConfiguration
import ILLMayaSpaceSwitcher.ILLMayaSpaceSwitcherManager

# For Development
from importlib import reload

print(f'Reloading {ILLMayaSpaceSwitcher.Util.__name__}')
reload(ILLMayaSpaceSwitcher.Util)

print(f'Reloading {ILLMayaSpaceSwitcher.ILLMayaSpaceSwitcherModel.__name__}')
reload(ILLMayaSpaceSwitcher.ILLMayaSpaceSwitcherModel)

print(f'Reloading {ILLMayaSpaceSwitcher.ILLMayaSpaceSwitcherAutoGenerator.__name__}')
reload(ILLMayaSpaceSwitcher.ILLMayaSpaceSwitcherAutoGenerator)

print(f'Reloading {ILLMayaSpaceSwitcher.ILLMayaSpaceSwitcherConfiguration.__name__}')
reload(ILLMayaSpaceSwitcher.ILLMayaSpaceSwitcherConfiguration)

print(f'Reloading {ILLMayaSpaceSwitcher.ILLMayaSpaceSwitcherManager.__name__}')
reload(ILLMayaSpaceSwitcher.ILLMayaSpaceSwitcherManager)
