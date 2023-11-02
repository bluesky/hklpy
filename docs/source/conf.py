# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

import pathlib
import sys

import sphinx_rtd_theme

docs_source = pathlib.Path(__file__).parent
sys.path.insert(0, str(docs_source.parent.parent))

# imports here for sphinx to build the documents without many WARNINGS.
import hkl
import hkl.calc
import hkl.diffract
import hkl.geometries
import hkl.user

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'hklpy'
copyright = '2014-2023, Brookhaven National Laboratory'
# author = 'Bluesky team'
version = hkl.__version__
release = version

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "sphinx.ext.coverage",
    "sphinx.ext.inheritance_diagram",
    "sphinx.ext.intersphinx",
    "sphinx.ext.mathjax",
    "sphinx.ext.napoleon",
    "sphinx.ext.viewcode",
    "nbsphinx",
]

templates_path = ['_templates']
exclude_patterns = ["**.ipynb_checkpoints"]


# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

sys.path.append(str(docs_source / "_themes"))
html_theme = "sphinx_rtd_theme"
html_theme_path = [sphinx_rtd_theme.get_html_theme_path()]
html_static_path = ['_static']


# -- Options for autodoc ---------------------------------------------------

autodoc_exclude_members = ",".join(
    """
    __weakref__
    _component_kinds
    _device_tuple
    _required_for_connection
    _sig_attrs
    _sub_devices
    calc_class
    component_names
    """.split()
)
autodoc_default_options = {
    #'members': 'var1, var2',
    #'member-order': 'bysource',
    "private-members": True,
    # "special-members": "__init__",
    # 'undoc-members': True,
    "exclude-members": autodoc_exclude_members,
}
autodoc_mock_imports = [
    "pint",
]

# Example configuration for intersphinx: refer to the Python standard library.
intersphinx_mapping = {"python": ("https://docs.python.org/3", None)}
inheritance_graph_attrs = dict(rankdir="LR")
inheritance_node_attrs = dict(fontsize=24)
autosummary_generate = True
