.. _user:

user
----

Make it easier for users (especially SPEC users) to learn and remember
the new tools in Bluesky's *hklpy* package.

.. TODO  will enable once more of these are provided

    Quick Reference Table

    ==============  =======================================
    *SPEC*          *hklpy*
    ==============  =======================================
    --              :func:`~calcUB`
    --              :func:`~newSample`
    --              :func:`~selectDiffractometer`
    ``br``          TODO:
    ``cal``         :func:`cahkl`
    ``cuts``        TODO: constraints
    ``cz``          TODO:
    ``freeze``      TODO: constraints
    ``g_sect``      TODO: constraints
    ``mz``          TODO:
    ``or_swap``     TODO:
    ``or0``         :func:`~setor`
    ``or1``         :func:`~setor`
    ``pa``          TODO: (`fourc.pa()`)
    ``pl``          TODO:
    ``reflex_beg``  TODO:
    ``reflex_end``  TODO:
    ``reflex``      TODO:
    ``setaz``       TODO:
    ``setlat``      :func:`~updateSample`
    ``setmode``     TODO: modes
    ``setsector``   TODO:
    ``sz``          TODO:
    ``unfreeze``    TODO: constraints
    ``wh``          :func:`~wh`
    ==============  =======================================

.. automodule:: hkl.user
    :members:

----

.. _user.examples:


EXAMPLES::

    # work with our 4-circle simulator
    selectDiffractometer(fourc)

    # sample is the silicon standard
    a0=5.4310196; newSample("silicon standard", a0, a0, a0, 90, 90, 90)

    listSamples()

    # define the first orientation reflection, specify each motor position
    # motor values given in "diffractometer order"::
    #     print(_geom_.calc.physical_axis_names)
    r1 = setor(4, 0, 0, -145.451, 0, 0, 69.0966, wavelength = 1.54)

    # move to the position of the second reflection: (040)
    %mov fourc.omega -145.451 fourc.chi 90 fourc.phi 0 fourc.tth 69.0966

    # define the second orientation reflection, use current motor positions
    r2 = setor(0, 4, 0)

    calcUB(r1, r2)

    # calculate reflection, record motor positions before and after
    p_before = fourc.real_position
    fourc.forward(4, 0, 0)
    p_after = fourc.real_position

    # show if the motors moved
    if p_before != p_after:
        print("fourc MOVED!")
    else:
        print("fourc did not move.")

    # cubic sample: show r2, the (040)
    fourc.inverse(-145.5, 90, 0, 69)
    # verify that the (0 -4 0) is half a rotation away in chi
    fourc.inverse(-145.5, -90, 0, 69)
