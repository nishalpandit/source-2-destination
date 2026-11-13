"""
Franchise Partner Views Bridge (franchise_views.py)
Source 2 Destination — Regional Operations Portal
Imports and bridges to franchise-views.py per AGENTS.md specification.
"""
import importlib
import sys

# Import implementation source module with hyphenated name
_impl = importlib.import_module("Source2Destination.franchise-views")

# Forward all public symbols from franchise-views into franchise_views namespace
for _attr in dir(_impl):
    if not _attr.startswith("__"):
        globals()[_attr] = getattr(_impl, _attr)
