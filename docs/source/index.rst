.. hklpy documentation master file

=====
hklpy
=====

Controls for using diffractometers within the `Bluesky Framework
<https://blueskyproject.io>`_.

Based on the *hkl* library (`documentation
<https://people.debian.org/~picca/hkl/hkl.html>`_, `source
<https://repo.or.cz/hkl.git>`_).  (Caution: Ignore the GitHub source `repository
<https://github.com/picca/hkl>`_)

.. ,
   with slightly cleaner abstractions
   when compared to the auto-generated gobject-introspection classes.

Integrates with `ophyd <https://blueskyproject.io/ophyd>`_ pseudopositioners
for use with `bluesky <https://blueskyproject.io/bluesky>`_ plans.

.. toctree::
   :glob:
   :hidden:

   overview
   install
   api
   ready_to_use
   examples/*
   constraints
   license
   release_notes

.. icons: https://fonts.google.com/icons

.. grid:: 3

    .. grid-item-card:: :material-outlined:`summarize;3em` :ref:`overview`

      Definitions, parts, usage, ...

    .. grid-item-card:: :material-regular:`install_desktop;3em` :ref:`install`

      How to install *hklpy*.

    .. grid-item-card:: :material-regular:`subscriptions;3em` :ref:`api_documentation`

      About the underlying devices and other support.

    .. grid-item-card:: :material-regular:`face;3em` :ref:`user`

      Make it easier for users.

    .. grid-item-card:: :material-regular:`precision_manufacturing;3em` :ref:`geometries`

      All the diffractometer geometries.

    .. grid-item-card:: :material-regular:`precision_manufacturing;3em` :ref:`ready_to_use`

      Simulated diffractometers, ready to use.

    .. grid-item-card:: :material-regular:`alt_route;3em` :ref:`examples`

      Example notebooks, how-to guides, ...

    .. grid-item-card:: :material-regular:`settings;3em` :ref:`configuration`

      Record the diffractometer configuration.

    .. grid-item-card:: :material-regular:`filter_list;3em` :ref:`constraints`

      Limit the number of reflections found.

    .. grid-item-card:: :material-regular:`toc;3em` :ref:`spec_commands_map`

      Bluesky for SPEC users.

    .. grid-item-card:: :material-regular:`history;3em` :ref:`release_notes`

      History of changes.

    .. grid-item-card:: :material-regular:`description;3em` :ref:`about`

      See below.

.. _about:

About
-----

:home: https://bluesky.github.io/hklpy
:source: https://github.com/bluesky/hklpy
:license: :ref:`license`
:full version: |release|
:published: |today|
:index: :ref:`genindex`
:module: :ref:`modindex`
