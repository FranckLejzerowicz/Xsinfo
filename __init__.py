# ----------------------------------------------------------------------------
# Copyright (c) 2022, Franck Lejzerowicz.
#
# Distributed under the terms of the Modified BSD License.
# ----------------------------------------------------------------------------

from ._version import get_versions

__version__ = get_versions()['version']
del get_versions

__all__ = ['Xsinfo']

