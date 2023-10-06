.. _spec_commands_map:

========================
SPEC commands in Bluesky
========================

Make it easier for users (especially SPEC users) to learn and remember
the new tools in Bluesky's *hklpy* package.

In addition to the comparison with SPEC commands, more *hklpy* commands
are listed in the :ref:`user` section.

.. index:: !Quick Reference Table

Quick Reference Table

==============  ==================================  ============
*SPEC*          *hklpy*                             description
==============  ==================================  ============
--              :func:`~calc_UB`                    Compute the UB matrix with two reflections.
--              :func:`~change_sample`              Pick a known sample to be the current selection.
--              :func:`~list_samples`               List all defined crystal samples.
--              :func:`~new_sample`                 Define a new crystal sample.
--              :func:`~select_diffractometer`      Select the default diffractometer.
``br h k l``    `DIFFRACTOMETER.move(h, k, l)`      move the diffractometer motors to the given :math:`h, k, l`.
``ca h k l``    `cahkl(h, k, l)`                    Prints calculated motor settings for the given :math:`h, k, l`.
``cuts``        TODO: constraints
``cz``          TODO:
``freeze``      TODO: constraints
``g_sect``      TODO: constraints
``mz``          TODO:
``or_swap``     `or_swap()`                         Exchange primary & secondary orientation reflections.
``or0``         :func:`~setor`                      Define a crystal reflection and its motor positions.
``or1``         :func:`~setor`                      Define a crystal reflection and its motor positions.
``pa``          :func:`~pa`                         Report all diffractometer settings.
``pl``          TODO:
``reflex_beg``  TODO:
``reflex_end``  TODO:
``reflex``      TODO:
``setaz``       TODO:
``setlat``      :func:`~update_sample(...)`         Update current sample lattice.
``setmode``     TODO: modes
``setsector``   TODO:
``sz``          TODO:
``unfreeze``    TODO: constraints
``wh``          :func:`~wh`                         Report (brief) where is the diffractometer.
==============  ==================================  ============
