"""
OpenLP Document Generator Package

This package provides utilities for generating documents and presentations
from OpenLP data.
"""

from .documenter import Documenter
from .imager import ImageError, Imager

__version__ = "0.1.0"
__all__ = ["Documenter", "Imager", "ImageError"]
