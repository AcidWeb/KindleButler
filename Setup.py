"""
py2exe build script for KindleButler.

Usage (Windows):
    python setup.py py2exe
"""
from sys import platform

NAME = "KindleButler"
VERSION = "0.2"
MAIN = "KindleButler.py"

if platform == "win32":
    # noinspection PyUnresolvedReferences
    import py2exe
    from distutils.core import setup
    additional_files = [('platforms', ['C:\Python34\Lib\site-packages\PyQt5\plugins\platforms\qwindows.dll']),
                        ('imageformats', ['C:\Python34\Lib\site-packages\PyQt5\plugins\imageformats\qico.dll']),
                        ('', ['LICENSE.txt',
                              'KindleButler.ini',
                              'C:\Python34\Lib\site-packages\PyQt5\libEGL.dll'])]
    extra_options = dict(
        options={'py2exe': {"bundle_files": 1,
                            "dll_excludes": ["tcl85.dll", "tk85.dll"],
                            "dist_dir": "dist",
                            "compressed": True,
                            "includes": ["sip"],
                            "excludes": ["tkinter"],
                            "optimize": 2}},
        windows=[{"script": "KindleButler.py",
                  "dest_base": "KindleButler",
                  "version": VERSION,
                  "copyright": "Pawel Jastrzebski © 2014",
                  "legal_copyright": "GNU General Public License (GPL-3)",
                  "product_version": VERSION,
                  "product_name": "KindleButler",
                  "file_description": "KindleButler",
                  "icon_resources": [(1, "Assets\KindleButler.ico")]}],
        zipfile=None,
        data_files=additional_files)
else:
    print('This script create only Windows releases.')
    exit()

#noinspection PyUnboundLocalVariable
setup(
    name=NAME,
    version=VERSION,
    author="Pawel Jastrzebski",
    author_email="pawelj@iosphe.re",
    description="KindleButler",
    license="GNU General Public License (GPL-3)",
    url="https://github.com/AcidWeb/KindleButler/",
    **extra_options
)