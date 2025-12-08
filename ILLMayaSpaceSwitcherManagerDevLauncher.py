import ILLMayaSpaceSwitcher.ILLMayaSpaceSwitcherManager

# For Development
import DevReloader
from importlib import reload

print(f'Reloading {DevReloader.__name__}')
reload(DevReloader)

# ILLMayaSpaceSwitcher.ILLMayaSpaceSwitcherManager.ILLMayaSpaceSwitcherManager.wipeSettings()
ILLMayaSpaceSwitcher.ILLMayaSpaceSwitcherManager.ILLMayaSpaceSwitcherManager.openMayaMainToolWindowInstance()
