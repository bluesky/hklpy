.. include:: /substitutions.txt

.. index:: SPEC; commands, hklpy; commands

.. _spec_commands_map:

========================
SPEC commands in Bluesky
========================

Make it easier for users (especially |spec| users) to learn and remember
the tools in Bluesky's |hklpy| package.

See section :ref:`user` for more |hklpy| commands.

.. index:: !Quick Reference Table

.. rubric:: Quick Reference Table

===============  =============================================================  ============
|spec|           |hklpy|                                                        description
===============  =============================================================  ============
--               :func:`~hkl.user.select_diffractometer`                        Select the default diffractometer.
``pa``           :func:`~hkl.user.pa`                                           Report (full) diffractometer settings.  (pa: print all)
``wh``           :func:`~hkl.user.wh`                                           Report (brief) diffractometer settings. (wh: where)
``br h k l``     ``d_object.move((h, k, l))``                                   (command line) Move motors of diffractometer ``d_object`` to the given :math:`h, k, l`.  Note the extra parenthesis.
``br h k l``     ``yield from bps.mv(d_object, (h, k, l))``                     (bluesky plan) Move motors of diffractometer ``d_object`` to the given :math:`h, k, l`.  Note the extra parenthesis.
``ca h k l``     :func:`~hkl.user.cahkl`                                        Prints calculated motor settings for the given :math:`h, k, l`.
``or_swap``      :func:`~hkl.user.or_swap()`                                    Exchange primary & secondary orientation reflections.
``or0``          :func:`~hkl.user.setor`                                        Define a crystal reflection and its motor positions.
``or1``          :func:`~hkl.user.setor`                                        Define a crystal reflection and its motor positions.
``reflex_beg``   :class:`~hkl.configuration.DiffractometerConfiguration`        Initializes the reflections file
``reflex_end``   :class:`~hkl.configuration.DiffractometerConfiguration`        Closes the reflections file
``reflex``       :class:`~hkl.configuration.DiffractometerConfiguration`        Adds reflections to the reflections file
``setlat``       :func:`~hkl.user.update_sample()`                              Update current sample lattice.
``setmode``      :func:`~hkl.engine.Engine.mode()`                              Set the diffractometer mode for the `forward()` computation.
--               :func:`~hkl.diffract.Diffractometer.show_constraints()`        Show the current set of constraints (cut points).
``cuts``         :func:`~hkl.diffract.Diffractometer.apply_constraints()`       Add constraints to the diffractometer `forward()` computation.
``freeze``       :func:`~hkl.diffract.Diffractometer.apply_constraints()`       Hold an axis constant during the diffractometer `forward()` computation.
``unfreeze``     :func:`~hkl.diffract.Diffractometer.undo_last_constraints()`   Undo the most-recent constraints applied.
--               :func:`~hkl.diffract.Diffractometer.reset_constraints()`       Reset the diffractometer constraints to defaults.
--               :func:`~hkl.user.calc_UB`                                      Compute the UB matrix with two reflections.
--               :func:`~hkl.user.change_sample`                                Pick a known sample to be the current selection.
--               :func:`~hkl.user.list_samples`                                 List all defined crystal samples.
--               :func:`~hkl.user.new_sample`                                   Define a new crystal sample.
``setaz h k l``  TODO:                                                          Set the azimuthal reference vector to the given :math:`h, k, l`.
``setsector``    TODO:                                                          Select a sector.
``cz``           TODO:                                                          Calculate zone from two reflections
``mz``           TODO:                                                          Move zone
``pl``           TODO:                                                          Set the scattering plane
``sz``           TODO:                                                          Set zone
``reflex``       TODO:                                                          Least squares refinement of lattice parameters from list of reflections
===============  =============================================================  ============
