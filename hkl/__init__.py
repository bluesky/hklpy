"""
:mod:`hkl` - HKL calculation utilities
======================================

.. module:: hkl
   :synopsis:

"""

import logging

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())

from ._version import get_versions  # noqa: F402, E402

__version__ = get_versions()["version"]
del get_versions
