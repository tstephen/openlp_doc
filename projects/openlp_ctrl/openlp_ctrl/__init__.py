"""
OpenLP Control package
"""

__version__ = "0.1.0"

from .connection_manager import ConnectionManager
from .server import app

__all__ = ["app", "ConnectionManager"]
