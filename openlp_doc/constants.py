"""
constants.py
"""

from importlib import metadata


class APP:
    NAME = "OpenLP song sheet"
    PACKAGE = __package__
    VSN = metadata.version(__package__)
