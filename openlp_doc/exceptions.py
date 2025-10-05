"""
exceptions.py
"""

from enum import Enum, unique


@unique
class Error(Enum):
    NONE = 0
    SCHEMA_INVALID = -101
    SEMANTIC_INVALID = -102
    DEPLOYMENT_INVALID = -103
    IMPL_EXISTING_FILE = -201
    IMPL_DUPE_ID = -202
    DEPLOY_FAILED = -400
    FAILED_AUTH = -401
    DEPLOY_BAD_CONFIG = -402
    DEPLOY_UNSUPPORTED_AUTH_TYPE = -403
    DEPLOY_UNSUPPORTED_APP = -405


class OpenLpException(Exception):
    def __init__(self, err):
        self.err = err
        super().__init__()

    def __str__(self):
        return f"{self.err}"
