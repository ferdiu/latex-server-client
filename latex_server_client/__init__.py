"""
LaTeX Compilation Server

A FastAPI-based HTTP server for compiling LaTeX documents to PDF.
"""

__version__ = "2.0.0"
__author__ = "Federico Manzella"
__email__ = "ferdiu.manzella@gmail.com"

from latex_server_client.latex_watch import LatexWatcher, LatexIgnore

__all__ = [
    "LatexWatcher",
    "LatexIgnore",
]
