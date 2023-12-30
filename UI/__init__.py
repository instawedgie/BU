"""
Simplifies loading for interface.py (ensure we don't forget something)
Used to import all .py files (except for __init__.py) in the directory
"""

from pathlib import Path
import importlib

__all__ = list(_.name[:-3] for _ in Path('UI').glob('*.py'))
# __all__.remove('__init__')

for module in __all__:
    importlib.import_module("UI" + "." + module)
