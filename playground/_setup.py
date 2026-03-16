"""
Shared Django bootstrap for playground scripts.

Usage:
    from _setup import *   # or just: import _setup
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "backend.settings")

import django
django.setup()
