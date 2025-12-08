from ILLMayaSpaceSwitcher import Util, ILLMayaSpaceSwitcherModel, ILLMayaSpaceSwitcherConfiguration, ILLMayaSpaceSwitcherManager

# For Development
from importlib import reload

print(f'Reloading {Util.__name__}')
reload(Util)

print(f'Reloading {ILLMayaSpaceSwitcherModel.__name__}')
reload(ILLMayaSpaceSwitcherModel)

print(f'Reloading {ILLMayaSpaceSwitcherConfiguration.__name__}')
reload(ILLMayaSpaceSwitcherConfiguration)

print(f'Reloading {ILLMayaSpaceSwitcherManager.__name__}')
reload(ILLMayaSpaceSwitcherManager)
