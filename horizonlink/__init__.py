"""HorizonLink research package."""

from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("horizonlink")
except PackageNotFoundError:  # Source tree used without installation.
    __version__ = "0+unknown"
