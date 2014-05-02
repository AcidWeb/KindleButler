"""
cx_Freeze build script for KindleButler.

Usage (Windows):
    python setup.py build
"""
from sys import platform

NAME = "KindleButler"
VERSION = "0.1"
MAIN = "KindleButler.py"

if platform == "win32":
    from cx_Freeze import setup, Executable
    extra_options = dict(
        options={"build_exe": {"optimize": 2,
                               "include_files": ['LICENSE.txt'],
                               "copy_dependent_files": True,
                               "create_shared_zip": False,
                               "append_script_to_exe": True,
                               "replace_paths": '*='}},
        executables=[Executable(MAIN,
                                base="Win32GUI",
                                targetName="KindleButler.exe",
                                icon="Assets/KindleButler.ico",
                                compress=False)])
else:
    print('This application work only on Windows.')
    exit()

#noinspection PyUnboundLocalVariable
setup(
    name=NAME,
    version=VERSION,
    author="Pawel Jastrzebski",
    author_email="pawelj@vulturis.eu",
    description="The tool that allows to easily send files to Kindle.",
    license="GNU General Public License (GPL-3)",
    url="https://github.com/AcidWeb/KindleButler/",
    **extra_options
)