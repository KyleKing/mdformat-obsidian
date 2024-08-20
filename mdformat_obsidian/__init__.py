"""An mdformat plugin for `obsidian`."""

__version__ = "0.1.0"

from .plugin import RENDERERS, update_mdit

__all__ = ("RENDERERS", "__version__", "update_mdit")
