import os
import sys

from scrapeomatic import __version__

sys.path.insert(0, os.path.abspath("../"))

version = __version__
project = "ScrapeOMatic"
copyright = "2023, Geniza Inc."
author = "Charles Givre"

extensions = ["sphinx.ext.autodoc", "sphinx.ext.coverage", "sphinx.ext.napoleon"]

templates_path = ["_templates"]

exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

html_theme = "sphinx_rtd_theme"
