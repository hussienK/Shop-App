import sys
from cx_Freeze import setup, Executable

# Dependencies are automatically detected, but it might need fine tuning.
# "packages": ["os"] is used as example only
build_exe_options = {"packages": ["os"], "excludes": ["tkinter"]}
buildOptions = dict(include_files = [('Resources')])

# base="Win32GUI" should be used only for Windows GUI app
base = None
if sys.platform == "win32":
    base = "Win32GUI"
    

setup(
    name = "guifoo",
    version = "0.1",
    description = "My GUI application!",
    options = dict(build_exe = buildOptions),
    executables = [Executable(script = "Shop Manager.py", base=base, icon="Resources/UI/Images/IndexIcon.ico"),Executable(script = "SearchSystem.py", base=base, icon="Resources/UI/Images/SearchIcon.ico"),Executable(script = "ItemCreator.py", base=base, icon="Resources/UI/Images/ItemCreatorIcon.ico"),Executable(script= "Inventorymanager.py", base=base, icon="Resources/UI/Images/InventoryIcon.ico"), Executable(script= "Extras.py", base=base, icon="Resources/UI/Images/DataIcon.ico"), Executable(script= "ToGetList.py", base=base, icon="Resources/UI/Images/ToGetIcon.ico")]
)