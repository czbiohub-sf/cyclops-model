"""DL model for analysis of OPS data at CZB SF"""

from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("cyclops_model")
except PackageNotFoundError:
    __version__ = "uninstalled"

__author__ = "Alex Hillsley"
__email__ = "avhillsley1@gmail.com"
