.. this page created by ./docs/make_geometry_tables.py

.. _geometry_tables:

=================================
Tables of Diffractometer Geometry
=================================

.. index:: mode

Tables are provided for the different geometries and then, for each geometry,
the calculation engines, pseudo axes required, modes of operation, and any
additional parameters required by the :ref:`mode <overview.mode>`.  The mode defines
which axes will be computed, which will be held constant, and any relationships
between axes.

Geometries indexed by number of circles
---------------------------------------

The different diffractometer geometries are distinguished, primarily, by
the number of axes (circles) and the names of each.  This table is
sorted first by the number of circles, and then the geometry name (as
used here in *hklpy*).


======== ================================================================ =======================================================================
#circles geometry                                                         real_axes
======== ================================================================ =======================================================================
4        :ref:`E4CH <E4CH_table>`                                         ``omega``, ``chi``, ``phi``, ``tth``
4        :ref:`E4CV <E4CV_table>`                                         ``omega``, ``chi``, ``phi``, ``tth``
4        :ref:`K4CV <K4CV_table>`                                         ``komega``, ``kappa``, ``kphi``, ``tth``
4        :ref:`PETRA3 P23 4C <PETRA3_P23_4C_table>`                       ``omega_t``, ``mu``, ``gamma``, ``delta``
4        :ref:`SOLEIL MARS <SOLEIL_MARS_table>`                           ``omega``, ``chi``, ``phi``, ``tth``
4        :ref:`SOLEIL SIXS MED1+2 <SOLEIL_SIXS_MED1+2_table>`             ``pitch``, ``mu``, ``gamma``, ``delta``
4        :ref:`ZAXIS <ZAXIS_table>`                                       ``mu``, ``omega``, ``delta``, ``gamma``
5        :ref:`SOLEIL SIXS MED2+2 <SOLEIL_SIXS_MED2+2_table>`             ``beta``, ``mu``, ``omega``, ``gamma``, ``delta``
5        :ref:`SOLEIL SIXS MED2+3 v2 <SOLEIL_SIXS_MED2+3_v2_table>`       ``mu``, ``omega``, ``gamma``, ``delta``, ``eta_a``
6        :ref:`E6C <E6C_table>`                                           ``mu``, ``omega``, ``chi``, ``phi``, ``gamma``, ``delta``
6        :ref:`K6C <K6C_table>`                                           ``mu``, ``komega``, ``kappa``, ``kphi``, ``gamma``, ``delta``
6        :ref:`PETRA3 P09 EH2 <PETRA3_P09_EH2_table>`                     ``mu``, ``omega``, ``chi``, ``phi``, ``delta``, ``gamma``
6        :ref:`SOLEIL NANOSCOPIUM ROBOT <SOLEIL_NANOSCOPIUM_ROBOT_table>` ``rz``, ``rs``, ``rx``, ``r``, ``delta``, ``gamma``
6        :ref:`SOLEIL SIRIUS KAPPA <SOLEIL_SIRIUS_KAPPA_table>`           ``mu``, ``komega``, ``kappa``, ``kphi``, ``delta``, ``gamma``
6        :ref:`SOLEIL SIRIUS TURRET <SOLEIL_SIRIUS_TURRET_table>`         ``basepitch``, ``thetah``, ``alphay``, ``alphax``, ``delta``, ``gamma``
6        :ref:`SOLEIL SIXS MED2+3 <SOLEIL_SIXS_MED2+3_table>`             ``beta``, ``mu``, ``omega``, ``gamma``, ``delta``, ``eta_a``
7        :ref:`PETRA3 P23 6C <PETRA3_P23_6C_table>`                       ``omega_t``, ``mu``, ``omega``, ``chi``, ``phi``, ``gamma``, ``delta``
======== ================================================================ =======================================================================



.. _geometry_tables.tables:

Tables for each geometry
------------------------

.. index:: mode

A table is provided for each diffractometer geometry listing the calculation
engines, pseudo axes required, modes of operation, and any additional parameters
required by the mode.

* *engine* : Defines the names (and order) of the pseudo axes.
* *pseudo axes* : The engine performs
  :meth:`~hkl.diffract.Diffractometer.forward()` (pseudo-to-real) and
  :meth:`~hkl.diffract.Diffractometer.inverse()` (real-to-pseudo)
  transformations between the real-space axes and the *pseudo* (typically
  reciprocal-space) axes.  The *engine* defines the *pseudo axes* to be used.
* *mode* : Defines which axes are used for the ``forward()`` computation.
* *axes read* : Axes used in the ``forward()`` computation.
* *axes written* : Axes computed by the ``forward()`` computation.
* *extra parameters* : Any necessary additional parameters.

.. index:: E4CH, geometry; E4CH

.. _E4CH_table:

Geometry: ``E4CH``
++++++++++++++++++

* real axes: ``omega``, ``chi``, ``phi``, ``tth``
* pseudo axes: depends on the engine

========= ========================== ================== ==================================== ==================================== ===============================
engine    pseudo axes                mode               axes read                            axes written                         extra parameters
========= ========================== ================== ==================================== ==================================== ===============================
emergence ``emergence``, ``azimuth`` emergence          ``omega``, ``chi``, ``phi``, ``tth``                                      ``x``, ``y``, ``z``
hkl       ``h``, ``k``, ``l``        bissector          ``omega``, ``chi``, ``phi``, ``tth`` ``omega``, ``chi``, ``phi``, ``tth``
hkl       ``h``, ``k``, ``l``        constant_chi       ``omega``, ``chi``, ``phi``, ``tth`` ``omega``, ``phi``, ``tth``
hkl       ``h``, ``k``, ``l``        constant_omega     ``omega``, ``chi``, ``phi``, ``tth`` ``chi``, ``phi``, ``tth``
hkl       ``h``, ``k``, ``l``        constant_phi       ``omega``, ``chi``, ``phi``, ``tth`` ``omega``, ``chi``, ``tth``
hkl       ``h``, ``k``, ``l``        double_diffraction ``omega``, ``chi``, ``phi``, ``tth`` ``omega``, ``chi``, ``phi``, ``tth`` ``h2``, ``k2``, ``l2``
hkl       ``h``, ``k``, ``l``        psi_constant       ``omega``, ``chi``, ``phi``, ``tth`` ``omega``, ``chi``, ``phi``, ``tth`` ``h2``, ``k2``, ``l2``, ``psi``
incidence ``incidence``, ``azimuth`` incidence          ``omega``, ``chi``, ``phi``                                               ``x``, ``y``, ``z``
psi       ``psi``                    psi                ``omega``, ``chi``, ``phi``, ``tth`` ``omega``, ``chi``, ``phi``, ``tth`` ``h2``, ``k2``, ``l2``
q         ``q``                      q                  ``tth``                              ``tth``
========= ========================== ================== ==================================== ==================================== ===============================

.. index:: E4CV, geometry; E4CV

.. _E4CV_table:

Geometry: ``E4CV``
++++++++++++++++++

* real axes: ``omega``, ``chi``, ``phi``, ``tth``
* pseudo axes: depends on the engine

========= ========================== ================== ==================================== ==================================== ===============================
engine    pseudo axes                mode               axes read                            axes written                         extra parameters
========= ========================== ================== ==================================== ==================================== ===============================
emergence ``emergence``, ``azimuth`` emergence          ``omega``, ``chi``, ``phi``, ``tth``                                      ``x``, ``y``, ``z``
hkl       ``h``, ``k``, ``l``        bissector          ``omega``, ``chi``, ``phi``, ``tth`` ``omega``, ``chi``, ``phi``, ``tth``
hkl       ``h``, ``k``, ``l``        constant_chi       ``omega``, ``chi``, ``phi``, ``tth`` ``omega``, ``phi``, ``tth``
hkl       ``h``, ``k``, ``l``        constant_omega     ``omega``, ``chi``, ``phi``, ``tth`` ``chi``, ``phi``, ``tth``
hkl       ``h``, ``k``, ``l``        constant_phi       ``omega``, ``chi``, ``phi``, ``tth`` ``omega``, ``chi``, ``tth``
hkl       ``h``, ``k``, ``l``        double_diffraction ``omega``, ``chi``, ``phi``, ``tth`` ``omega``, ``chi``, ``phi``, ``tth`` ``h2``, ``k2``, ``l2``
hkl       ``h``, ``k``, ``l``        psi_constant       ``omega``, ``chi``, ``phi``, ``tth`` ``omega``, ``chi``, ``phi``, ``tth`` ``h2``, ``k2``, ``l2``, ``psi``
incidence ``incidence``, ``azimuth`` incidence          ``omega``, ``chi``, ``phi``                                               ``x``, ``y``, ``z``
psi       ``psi``                    psi                ``omega``, ``chi``, ``phi``, ``tth`` ``omega``, ``chi``, ``phi``, ``tth`` ``h2``, ``k2``, ``l2``
q         ``q``                      q                  ``tth``                              ``tth``
========= ========================== ================== ==================================== ==================================== ===============================

.. index:: E6C, geometry; E6C

.. _E6C_table:

Geometry: ``E6C``
+++++++++++++++++

* real axes: ``mu``, ``omega``, ``chi``, ``phi``, ``gamma``, ``delta``
* pseudo axes: depends on the engine

========= ========================== ============================= ========================================================= ============================================== ===============================
engine    pseudo axes                mode                          axes read                                                 axes written                                   extra parameters
========= ========================== ============================= ========================================================= ============================================== ===============================
emergence ``emergence``, ``azimuth`` emergence                     ``mu``, ``omega``, ``chi``, ``phi``, ``gamma``, ``delta``                                                ``x``, ``y``, ``z``
hkl       ``h``, ``k``, ``l``        bissector_horizontal          ``mu``, ``omega``, ``chi``, ``phi``, ``gamma``, ``delta`` ``mu``, ``omega``, ``chi``, ``phi``, ``gamma``
hkl       ``h``, ``k``, ``l``        bissector_vertical            ``mu``, ``omega``, ``chi``, ``phi``, ``gamma``, ``delta`` ``omega``, ``chi``, ``phi``, ``delta``
hkl       ``h``, ``k``, ``l``        constant_chi_vertical         ``mu``, ``omega``, ``chi``, ``phi``, ``gamma``, ``delta`` ``omega``, ``phi``, ``delta``
hkl       ``h``, ``k``, ``l``        constant_mu_horizontal        ``mu``, ``omega``, ``chi``, ``phi``, ``gamma``, ``delta`` ``chi``, ``phi``, ``gamma``
hkl       ``h``, ``k``, ``l``        constant_omega_vertical       ``mu``, ``omega``, ``chi``, ``phi``, ``gamma``, ``delta`` ``chi``, ``phi``, ``delta``
hkl       ``h``, ``k``, ``l``        constant_phi_vertical         ``mu``, ``omega``, ``chi``, ``phi``, ``gamma``, ``delta`` ``omega``, ``chi``, ``delta``
hkl       ``h``, ``k``, ``l``        double_diffraction_horizontal ``mu``, ``omega``, ``chi``, ``phi``, ``gamma``, ``delta`` ``mu``, ``chi``, ``phi``, ``gamma``            ``h2``, ``k2``, ``l2``
hkl       ``h``, ``k``, ``l``        double_diffraction_vertical   ``mu``, ``omega``, ``chi``, ``phi``, ``gamma``, ``delta`` ``omega``, ``chi``, ``phi``, ``delta``         ``h2``, ``k2``, ``l2``
hkl       ``h``, ``k``, ``l``        lifting_detector_mu           ``mu``, ``omega``, ``chi``, ``phi``, ``gamma``, ``delta`` ``mu``, ``gamma``, ``delta``
hkl       ``h``, ``k``, ``l``        lifting_detector_omega        ``mu``, ``omega``, ``chi``, ``phi``, ``gamma``, ``delta`` ``omega``, ``gamma``, ``delta``
hkl       ``h``, ``k``, ``l``        lifting_detector_phi          ``mu``, ``omega``, ``chi``, ``phi``, ``gamma``, ``delta`` ``phi``, ``gamma``, ``delta``
hkl       ``h``, ``k``, ``l``        psi_constant_horizontal       ``mu``, ``omega``, ``chi``, ``phi``, ``gamma``, ``delta`` ``omega``, ``chi``, ``phi``, ``gamma``         ``h2``, ``k2``, ``l2``, ``psi``
hkl       ``h``, ``k``, ``l``        psi_constant_vertical         ``mu``, ``omega``, ``chi``, ``phi``, ``gamma``, ``delta`` ``omega``, ``chi``, ``phi``, ``delta``         ``h2``, ``k2``, ``l2``, ``psi``
incidence ``incidence``, ``azimuth`` incidence                     ``mu``, ``omega``, ``chi``, ``phi``                                                                      ``x``, ``y``, ``z``
psi       ``psi``                    psi_vertical                  ``mu``, ``omega``, ``chi``, ``phi``, ``gamma``, ``delta`` ``omega``, ``chi``, ``phi``, ``delta``         ``h2``, ``k2``, ``l2``
q2        ``q``, ``alpha``           q2                            ``gamma``, ``delta``                                      ``gamma``, ``delta``
qper_qpar ``qper``, ``qpar``         qper_qpar                     ``gamma``, ``delta``                                      ``gamma``, ``delta``                           ``x``, ``y``, ``z``
tth2      ``tth``, ``alpha``         tth2                          ``gamma``, ``delta``                                      ``gamma``, ``delta``
========= ========================== ============================= ========================================================= ============================================== ===============================

.. index:: K4CV, geometry; K4CV

.. _K4CV_table:

Geometry: ``K4CV``
++++++++++++++++++

* real axes: ``komega``, ``kappa``, ``kphi``, ``tth``
* pseudo axes: depends on the engine

========= =========================== ================== ======================================== ======================================== ===============================
engine    pseudo axes                 mode               axes read                                axes written                             extra parameters
========= =========================== ================== ======================================== ======================================== ===============================
emergence ``emergence``, ``azimuth``  emergence          ``komega``, ``kappa``, ``kphi``, ``tth``                                          ``x``, ``y``, ``z``
eulerians ``omega``, ``chi``, ``phi`` eulerians          ``komega``, ``kappa``, ``kphi``          ``komega``, ``kappa``, ``kphi``          ``solutions``
hkl       ``h``, ``k``, ``l``         bissector          ``komega``, ``kappa``, ``kphi``, ``tth`` ``komega``, ``kappa``, ``kphi``, ``tth``
hkl       ``h``, ``k``, ``l``         constant_chi       ``komega``, ``kappa``, ``kphi``, ``tth`` ``komega``, ``kappa``, ``kphi``, ``tth`` ``chi``
hkl       ``h``, ``k``, ``l``         constant_omega     ``komega``, ``kappa``, ``kphi``, ``tth`` ``komega``, ``kappa``, ``kphi``, ``tth`` ``omega``
hkl       ``h``, ``k``, ``l``         constant_phi       ``komega``, ``kappa``, ``kphi``, ``tth`` ``komega``, ``kappa``, ``kphi``, ``tth`` ``phi``
hkl       ``h``, ``k``, ``l``         double_diffraction ``komega``, ``kappa``, ``kphi``, ``tth`` ``komega``, ``kappa``, ``kphi``, ``tth`` ``h2``, ``k2``, ``l2``
hkl       ``h``, ``k``, ``l``         psi_constant       ``komega``, ``kappa``, ``kphi``, ``tth`` ``komega``, ``kappa``, ``kphi``, ``tth`` ``h2``, ``k2``, ``l2``, ``psi``
incidence ``incidence``, ``azimuth``  incidence          ``komega``, ``kappa``, ``kphi``                                                   ``x``, ``y``, ``z``
psi       ``psi``                     psi                ``komega``, ``kappa``, ``kphi``, ``tth`` ``komega``, ``kappa``, ``kphi``, ``tth`` ``h2``, ``k2``, ``l2``
q         ``q``                       q                  ``tth``                                  ``tth``
========= =========================== ================== ======================================== ======================================== ===============================

.. index:: K6C, geometry; K6C

.. _K6C_table:

Geometry: ``K6C``
+++++++++++++++++

* real axes: ``mu``, ``komega``, ``kappa``, ``kphi``, ``gamma``, ``delta``
* pseudo axes: depends on the engine

========= =========================== ============================= ============================================================= ===================================================== ===============================================
engine    pseudo axes                 mode                          axes read                                                     axes written                                          extra parameters
========= =========================== ============================= ============================================================= ===================================================== ===============================================
emergence ``emergence``, ``azimuth``  emergence                     ``mu``, ``komega``, ``kappa``, ``kphi``, ``gamma``, ``delta``                                                       ``x``, ``y``, ``z``
eulerians ``omega``, ``chi``, ``phi`` eulerians                     ``komega``, ``kappa``, ``kphi``                               ``komega``, ``kappa``, ``kphi``                       ``solutions``
hkl       ``h``, ``k``, ``l``         bissector_horizontal          ``mu``, ``komega``, ``kappa``, ``kphi``, ``gamma``, ``delta`` ``mu``, ``komega``, ``kappa``, ``kphi``, ``gamma``
hkl       ``h``, ``k``, ``l``         bissector_vertical            ``mu``, ``komega``, ``kappa``, ``kphi``, ``gamma``, ``delta`` ``komega``, ``kappa``, ``kphi``, ``delta``
hkl       ``h``, ``k``, ``l``         constant_chi_vertical         ``mu``, ``komega``, ``kappa``, ``kphi``, ``gamma``, ``delta`` ``komega``, ``kappa``, ``kphi``, ``delta``            ``chi``
hkl       ``h``, ``k``, ``l``         constant_incidence            ``mu``, ``komega``, ``kappa``, ``kphi``, ``gamma``, ``delta`` ``komega``, ``kappa``, ``kphi``, ``gamma``, ``delta`` ``x``, ``y``, ``z``, ``incidence``, ``azimuth``
hkl       ``h``, ``k``, ``l``         constant_kphi_horizontal      ``mu``, ``komega``, ``kappa``, ``kphi``, ``gamma``, ``delta`` ``mu``, ``komega``, ``kappa``, ``gamma``
hkl       ``h``, ``k``, ``l``         constant_omega_vertical       ``mu``, ``komega``, ``kappa``, ``kphi``, ``gamma``, ``delta`` ``komega``, ``kappa``, ``kphi``, ``delta``            ``omega``
hkl       ``h``, ``k``, ``l``         constant_phi_horizontal       ``mu``, ``komega``, ``kappa``, ``kphi``, ``gamma``, ``delta`` ``mu``, ``komega``, ``kappa``, ``kphi``, ``gamma``    ``phi``
hkl       ``h``, ``k``, ``l``         constant_phi_vertical         ``mu``, ``komega``, ``kappa``, ``kphi``, ``gamma``, ``delta`` ``komega``, ``kappa``, ``kphi``, ``delta``            ``phi``
hkl       ``h``, ``k``, ``l``         double_diffraction_horizontal ``mu``, ``komega``, ``kappa``, ``kphi``, ``gamma``, ``delta`` ``mu``, ``komega``, ``kappa``, ``kphi``, ``gamma``    ``h2``, ``k2``, ``l2``
hkl       ``h``, ``k``, ``l``         double_diffraction_vertical   ``mu``, ``komega``, ``kappa``, ``kphi``, ``gamma``, ``delta`` ``komega``, ``kappa``, ``kphi``, ``delta``            ``h2``, ``k2``, ``l2``
hkl       ``h``, ``k``, ``l``         lifting_detector_komega       ``mu``, ``komega``, ``kappa``, ``kphi``, ``gamma``, ``delta`` ``komega``, ``gamma``, ``delta``
hkl       ``h``, ``k``, ``l``         lifting_detector_kphi         ``mu``, ``komega``, ``kappa``, ``kphi``, ``gamma``, ``delta`` ``kphi``, ``gamma``, ``delta``
hkl       ``h``, ``k``, ``l``         lifting_detector_mu           ``mu``, ``komega``, ``kappa``, ``kphi``, ``gamma``, ``delta`` ``mu``, ``gamma``, ``delta``
hkl       ``h``, ``k``, ``l``         psi_constant_vertical         ``mu``, ``komega``, ``kappa``, ``kphi``, ``gamma``, ``delta`` ``komega``, ``kappa``, ``kphi``, ``delta``            ``h2``, ``k2``, ``l2``, ``psi``
incidence ``incidence``, ``azimuth``  incidence                     ``mu``, ``komega``, ``kappa``, ``kphi``                                                                             ``x``, ``y``, ``z``
psi       ``psi``                     psi_vertical                  ``mu``, ``komega``, ``kappa``, ``kphi``, ``gamma``, ``delta`` ``komega``, ``kappa``, ``kphi``, ``delta``            ``h2``, ``k2``, ``l2``
q2        ``q``, ``alpha``            q2                            ``gamma``, ``delta``                                          ``gamma``, ``delta``
qper_qpar ``qper``, ``qpar``          qper_qpar                     ``gamma``, ``delta``                                          ``gamma``, ``delta``                                  ``x``, ``y``, ``z``
tth2      ``tth``, ``alpha``          tth2                          ``gamma``, ``delta``                                          ``gamma``, ``delta``
========= =========================== ============================= ============================================================= ===================================================== ===============================================

.. index:: PETRA3_P09_EH2, geometry; PETRA3_P09_EH2

.. _PETRA3_P09_EH2_table:

Geometry: ``PETRA3 P09 EH2``
++++++++++++++++++++++++++++

* real axes: ``mu``, ``omega``, ``chi``, ``phi``, ``delta``, ``gamma``
* pseudo axes: depends on the engine

====== =================== =================================== ========================================================= ======================================= ================
engine pseudo axes         mode                                axes read                                                 axes written                            extra parameters
====== =================== =================================== ========================================================= ======================================= ================
hkl    ``h``, ``k``, ``l`` 4-circles bissecting horizontal     ``mu``, ``omega``, ``chi``, ``phi``, ``delta``, ``gamma`` ``omega``, ``chi``, ``phi``, ``delta``
hkl    ``h``, ``k``, ``l`` 4-circles constant chi horizontal   ``mu``, ``omega``, ``chi``, ``phi``, ``delta``, ``gamma`` ``omega``, ``phi``, ``delta``
hkl    ``h``, ``k``, ``l`` 4-circles constant omega horizontal ``mu``, ``omega``, ``chi``, ``phi``, ``delta``, ``gamma`` ``chi``, ``phi``, ``delta``
hkl    ``h``, ``k``, ``l`` 4-circles constant phi horizontal   ``mu``, ``omega``, ``chi``, ``phi``, ``delta``, ``gamma`` ``omega``, ``chi``, ``delta``
hkl    ``h``, ``k``, ``l`` lifting detector chi                ``mu``, ``omega``, ``chi``, ``phi``, ``delta``, ``gamma`` ``chi``, ``delta``, ``gamma``
hkl    ``h``, ``k``, ``l`` lifting detector mu                 ``mu``, ``omega``, ``chi``, ``phi``, ``delta``, ``gamma`` ``mu``, ``delta``, ``gamma``
hkl    ``h``, ``k``, ``l`` lifting detector omega              ``mu``, ``omega``, ``chi``, ``phi``, ``delta``, ``gamma`` ``omega``, ``delta``, ``gamma``
hkl    ``h``, ``k``, ``l`` lifting detector phi                ``mu``, ``omega``, ``chi``, ``phi``, ``delta``, ``gamma`` ``phi``, ``delta``, ``gamma``
hkl    ``h``, ``k``, ``l`` zaxis + alpha-fixed                 ``mu``, ``omega``, ``chi``, ``phi``, ``delta``, ``gamma`` ``omega``, ``delta``, ``gamma``
hkl    ``h``, ``k``, ``l`` zaxis + alpha=beta                  ``mu``, ``omega``, ``chi``, ``phi``, ``delta``, ``gamma`` ``mu``, ``omega``, ``delta``, ``gamma``
hkl    ``h``, ``k``, ``l`` zaxis + beta-fixed                  ``mu``, ``omega``, ``chi``, ``phi``, ``delta``, ``gamma`` ``mu``, ``delta``, ``gamma``
====== =================== =================================== ========================================================= ======================================= ================

.. index:: PETRA3_P23_4C, geometry; PETRA3_P23_4C

.. _PETRA3_P23_4C_table:

Geometry: ``PETRA3 P23 4C``
+++++++++++++++++++++++++++

* real axes: ``omega_t``, ``mu``, ``gamma``, ``delta``
* pseudo axes: depends on the engine

========= ========================== ======================== ========================================= ========================================= ===============================
engine    pseudo axes                mode                     axes read                                 axes written                              extra parameters
========= ========================== ======================== ========================================= ========================================= ===============================
emergence ``emergence``, ``azimuth`` emergence                ``omega_t``, ``mu``, ``gamma``, ``delta``                                           ``x``, ``y``, ``z``
hkl       ``h``, ``k``, ``l``        bissector_horizontal     ``omega_t``, ``mu``, ``gamma``, ``delta`` ``omega_t``, ``mu``, ``gamma``
hkl       ``h``, ``k``, ``l``        bissector_vertical       ``omega_t``, ``mu``, ``gamma``, ``delta`` ``omega_t``, ``mu``, ``delta``
hkl       ``h``, ``k``, ``l``        lifting_detector_mu      ``omega_t``, ``mu``, ``gamma``, ``delta`` ``mu``, ``gamma``, ``delta``
hkl       ``h``, ``k``, ``l``        lifting_detector_omega_t ``omega_t``, ``mu``, ``gamma``, ``delta`` ``omega_t``, ``gamma``, ``delta``
hkl       ``h``, ``k``, ``l``        psi_constant             ``omega_t``, ``mu``, ``gamma``, ``delta`` ``omega_t``, ``mu``, ``gamma``, ``delta`` ``h2``, ``k2``, ``l2``, ``psi``
incidence ``incidence``, ``azimuth`` incidence                ``omega_t``, ``mu``                                                                 ``x``, ``y``, ``z``
q2        ``q``, ``alpha``           q2                       ``gamma``, ``delta``                      ``gamma``, ``delta``
qper_qpar ``qper``, ``qpar``         qper_qpar                ``gamma``, ``delta``                      ``gamma``, ``delta``                      ``x``, ``y``, ``z``
tth2      ``tth``, ``alpha``         tth2                     ``gamma``, ``delta``                      ``gamma``, ``delta``
========= ========================== ======================== ========================================= ========================================= ===============================

.. index:: PETRA3_P23_6C, geometry; PETRA3_P23_6C

.. _PETRA3_P23_6C_table:

Geometry: ``PETRA3 P23 6C``
+++++++++++++++++++++++++++

* real axes: ``omega_t``, ``mu``, ``omega``, ``chi``, ``phi``, ``gamma``, ``delta``
* pseudo axes: depends on the engine

========= ========================== ============================= ====================================================================== ============================================== ===============================
engine    pseudo axes                mode                          axes read                                                              axes written                                   extra parameters
========= ========================== ============================= ====================================================================== ============================================== ===============================
emergence ``emergence``, ``azimuth`` emergence                     ``omega_t``, ``mu``, ``omega``, ``chi``, ``phi``, ``gamma``, ``delta``                                                ``x``, ``y``, ``z``
hkl       ``h``, ``k``, ``l``        bissector_horizontal          ``omega_t``, ``mu``, ``omega``, ``chi``, ``phi``, ``gamma``, ``delta`` ``mu``, ``omega``, ``chi``, ``phi``, ``gamma``
hkl       ``h``, ``k``, ``l``        bissector_vertical            ``omega_t``, ``mu``, ``omega``, ``chi``, ``phi``, ``gamma``, ``delta`` ``omega``, ``chi``, ``phi``, ``delta``
hkl       ``h``, ``k``, ``l``        constant_chi_vertical         ``omega_t``, ``mu``, ``omega``, ``chi``, ``phi``, ``gamma``, ``delta`` ``omega``, ``phi``, ``delta``
hkl       ``h``, ``k``, ``l``        constant_mu_horizontal        ``omega_t``, ``mu``, ``omega``, ``chi``, ``phi``, ``gamma``, ``delta`` ``chi``, ``phi``, ``gamma``
hkl       ``h``, ``k``, ``l``        constant_omega_vertical       ``omega_t``, ``mu``, ``omega``, ``chi``, ``phi``, ``gamma``, ``delta`` ``chi``, ``phi``, ``delta``
hkl       ``h``, ``k``, ``l``        constant_phi_vertical         ``omega_t``, ``mu``, ``omega``, ``chi``, ``phi``, ``gamma``, ``delta`` ``omega``, ``chi``, ``delta``
hkl       ``h``, ``k``, ``l``        double_diffraction_horizontal ``omega_t``, ``mu``, ``omega``, ``chi``, ``phi``, ``gamma``, ``delta`` ``mu``, ``chi``, ``phi``, ``gamma``            ``h2``, ``k2``, ``l2``
hkl       ``h``, ``k``, ``l``        double_diffraction_vertical   ``omega_t``, ``mu``, ``omega``, ``chi``, ``phi``, ``gamma``, ``delta`` ``omega``, ``chi``, ``phi``, ``delta``         ``h2``, ``k2``, ``l2``
hkl       ``h``, ``k``, ``l``        lifting_detector_mu           ``omega_t``, ``mu``, ``omega``, ``chi``, ``phi``, ``gamma``, ``delta`` ``mu``, ``gamma``, ``delta``
hkl       ``h``, ``k``, ``l``        lifting_detector_omega        ``omega_t``, ``mu``, ``omega``, ``chi``, ``phi``, ``gamma``, ``delta`` ``omega``, ``gamma``, ``delta``
hkl       ``h``, ``k``, ``l``        lifting_detector_phi          ``omega_t``, ``mu``, ``omega``, ``chi``, ``phi``, ``gamma``, ``delta`` ``phi``, ``gamma``, ``delta``
hkl       ``h``, ``k``, ``l``        psi_constant_horizontal       ``omega_t``, ``mu``, ``omega``, ``chi``, ``phi``, ``gamma``, ``delta`` ``omega``, ``chi``, ``phi``, ``gamma``         ``h2``, ``k2``, ``l2``, ``psi``
hkl       ``h``, ``k``, ``l``        psi_constant_vertical         ``omega_t``, ``mu``, ``omega``, ``chi``, ``phi``, ``gamma``, ``delta`` ``omega``, ``chi``, ``phi``, ``delta``         ``h2``, ``k2``, ``l2``, ``psi``
incidence ``incidence``, ``azimuth`` incidence                     ``omega_t``, ``mu``, ``omega``, ``chi``, ``phi``                                                                      ``x``, ``y``, ``z``
psi       ``psi``                    psi_vertical                  ``omega_t``, ``mu``, ``omega``, ``chi``, ``phi``, ``gamma``, ``delta`` ``omega``, ``chi``, ``phi``, ``delta``         ``h2``, ``k2``, ``l2``
q2        ``q``, ``alpha``           q2                            ``gamma``, ``delta``                                                   ``gamma``, ``delta``
qper_qpar ``qper``, ``qpar``         qper_qpar                     ``gamma``, ``delta``                                                   ``gamma``, ``delta``                           ``x``, ``y``, ``z``
tth2      ``tth``, ``alpha``         tth2                          ``gamma``, ``delta``                                                   ``gamma``, ``delta``
========= ========================== ============================= ====================================================================== ============================================== ===============================

.. index:: SOLEIL_MARS, geometry; SOLEIL_MARS

.. _SOLEIL_MARS_table:

Geometry: ``SOLEIL MARS``
+++++++++++++++++++++++++

* real axes: ``omega``, ``chi``, ``phi``, ``tth``
* pseudo axes: depends on the engine

========= ========================== ================== ==================================== ==================================== ===============================
engine    pseudo axes                mode               axes read                            axes written                         extra parameters
========= ========================== ================== ==================================== ==================================== ===============================
emergence ``emergence``, ``azimuth`` emergence          ``omega``, ``chi``, ``phi``, ``tth``                                      ``x``, ``y``, ``z``
hkl       ``h``, ``k``, ``l``        bissector          ``omega``, ``chi``, ``phi``, ``tth`` ``omega``, ``chi``, ``phi``, ``tth``
hkl       ``h``, ``k``, ``l``        constant_chi       ``omega``, ``chi``, ``phi``, ``tth`` ``omega``, ``phi``, ``tth``
hkl       ``h``, ``k``, ``l``        constant_omega     ``omega``, ``chi``, ``phi``, ``tth`` ``chi``, ``phi``, ``tth``
hkl       ``h``, ``k``, ``l``        constant_phi       ``omega``, ``chi``, ``phi``, ``tth`` ``omega``, ``chi``, ``tth``
hkl       ``h``, ``k``, ``l``        double_diffraction ``omega``, ``chi``, ``phi``, ``tth`` ``omega``, ``chi``, ``phi``, ``tth`` ``h2``, ``k2``, ``l2``
hkl       ``h``, ``k``, ``l``        psi_constant       ``omega``, ``chi``, ``phi``, ``tth`` ``omega``, ``chi``, ``phi``, ``tth`` ``h2``, ``k2``, ``l2``, ``psi``
incidence ``incidence``, ``azimuth`` incidence          ``omega``, ``chi``, ``phi``                                               ``x``, ``y``, ``z``
psi       ``psi``                    psi                ``omega``, ``chi``, ``phi``, ``tth`` ``omega``, ``chi``, ``phi``, ``tth`` ``h2``, ``k2``, ``l2``
q         ``q``                      q                  ``tth``                              ``tth``
========= ========================== ================== ==================================== ==================================== ===============================

.. index:: SOLEIL_NANOSCOPIUM_ROBOT, geometry; SOLEIL_NANOSCOPIUM_ROBOT

.. _SOLEIL_NANOSCOPIUM_ROBOT_table:

Geometry: ``SOLEIL NANOSCOPIUM ROBOT``
++++++++++++++++++++++++++++++++++++++

* real axes: ``rz``, ``rs``, ``rx``, ``r``, ``delta``, ``gamma``
* pseudo axes: depends on the engine

====== =================== =================== =================================================== ============================ ================
engine pseudo axes         mode                axes read                                           axes written                 extra parameters
====== =================== =================== =================================================== ============================ ================
hkl    ``h``, ``k``, ``l`` lifting detector rs ``rz``, ``rs``, ``rx``, ``r``, ``delta``, ``gamma`` ``rs``, ``delta``, ``gamma``
hkl    ``h``, ``k``, ``l`` lifting detector rx ``rz``, ``rs``, ``rx``, ``r``, ``delta``, ``gamma`` ``rx``, ``delta``, ``gamma``
hkl    ``h``, ``k``, ``l`` lifting detector rz ``rz``, ``rs``, ``rx``, ``r``, ``delta``, ``gamma`` ``rz``, ``delta``, ``gamma``
====== =================== =================== =================================================== ============================ ================

.. index:: SOLEIL_SIRIUS_KAPPA, geometry; SOLEIL_SIRIUS_KAPPA

.. _SOLEIL_SIRIUS_KAPPA_table:

Geometry: ``SOLEIL SIRIUS KAPPA``
+++++++++++++++++++++++++++++++++

* real axes: ``mu``, ``komega``, ``kappa``, ``kphi``, ``delta``, ``gamma``
* pseudo axes: depends on the engine

========= =========================== ================================ ============================================================= ===================================================== ===============================================
engine    pseudo axes                 mode                             axes read                                                     axes written                                          extra parameters
========= =========================== ================================ ============================================================= ===================================================== ===============================================
emergence ``emergence``, ``azimuth``  emergence                        ``mu``, ``komega``, ``kappa``, ``kphi``, ``gamma``, ``delta``                                                       ``x``, ``y``, ``z``
eulerians ``omega``, ``chi``, ``phi`` eulerians                        ``komega``, ``kappa``, ``kphi``                               ``komega``, ``kappa``, ``kphi``                       ``solutions``
hkl       ``h``, ``k``, ``l``         bissector_horizontal             ``mu``, ``komega``, ``kappa``, ``kphi``, ``delta``, ``gamma`` ``mu``, ``komega``, ``kappa``, ``kphi``, ``delta``
hkl       ``h``, ``k``, ``l``         bissector_vertical               ``mu``, ``komega``, ``kappa``, ``kphi``, ``delta``, ``gamma`` ``komega``, ``kappa``, ``kphi``, ``gamma``
hkl       ``h``, ``k``, ``l``         constant_chi_vertical            ``mu``, ``komega``, ``kappa``, ``kphi``, ``delta``, ``gamma`` ``komega``, ``kappa``, ``kphi``, ``gamma``            ``chi``
hkl       ``h``, ``k``, ``l``         constant_incidence               ``mu``, ``komega``, ``kappa``, ``kphi``, ``delta``, ``gamma`` ``komega``, ``kappa``, ``kphi``, ``delta``, ``gamma`` ``x``, ``y``, ``z``, ``incidence``, ``azimuth``
hkl       ``h``, ``k``, ``l``         constant_kphi_horizontal         ``mu``, ``komega``, ``kappa``, ``kphi``, ``delta``, ``gamma`` ``mu``, ``komega``, ``kappa``, ``delta``
hkl       ``h``, ``k``, ``l``         constant_omega_vertical          ``mu``, ``komega``, ``kappa``, ``kphi``, ``delta``, ``gamma`` ``komega``, ``kappa``, ``kphi``, ``gamma``            ``omega``
hkl       ``h``, ``k``, ``l``         constant_phi_horizontal          ``mu``, ``komega``, ``kappa``, ``kphi``, ``delta``, ``gamma`` ``mu``, ``komega``, ``kappa``, ``kphi``, ``delta``    ``phi``
hkl       ``h``, ``k``, ``l``         constant_phi_vertical            ``mu``, ``komega``, ``kappa``, ``kphi``, ``delta``, ``gamma`` ``komega``, ``kappa``, ``kphi``, ``gamma``            ``phi``
hkl       ``h``, ``k``, ``l``         double_diffraction_horizontal    ``mu``, ``komega``, ``kappa``, ``kphi``, ``delta``, ``gamma`` ``mu``, ``komega``, ``kappa``, ``kphi``, ``delta``    ``h2``, ``k2``, ``l2``
hkl       ``h``, ``k``, ``l``         double_diffraction_vertical      ``mu``, ``komega``, ``kappa``, ``kphi``, ``delta``, ``gamma`` ``komega``, ``kappa``, ``kphi``, ``gamma``            ``h2``, ``k2``, ``l2``
hkl       ``h``, ``k``, ``l``         lifting_detector_komega          ``mu``, ``komega``, ``kappa``, ``kphi``, ``delta``, ``gamma`` ``komega``, ``delta``, ``gamma``
hkl       ``h``, ``k``, ``l``         lifting_detector_kphi            ``mu``, ``komega``, ``kappa``, ``kphi``, ``delta``, ``gamma`` ``kphi``, ``delta``, ``gamma``
hkl       ``h``, ``k``, ``l``         lifting_detector_mu              ``mu``, ``komega``, ``kappa``, ``kphi``, ``delta``, ``gamma`` ``mu``, ``delta``, ``gamma``
hkl       ``h``, ``k``, ``l``         psi_constant_vertical            ``mu``, ``komega``, ``kappa``, ``kphi``, ``delta``, ``gamma`` ``komega``, ``kappa``, ``kphi``, ``gamma``            ``h2``, ``k2``, ``l2``, ``psi``
incidence ``incidence``, ``azimuth``  incidence                        ``mu``, ``komega``, ``kappa``, ``kphi``                                                                             ``x``, ``y``, ``z``
psi       ``psi``                     psi_vertical_soleil_sirius_kappa ``mu``, ``komega``, ``kappa``, ``kphi``, ``delta``, ``gamma`` ``komega``, ``kappa``, ``kphi``, ``gamma``            ``h2``, ``k2``, ``l2``
q2        ``q``, ``alpha``            q2                               ``gamma``, ``delta``                                          ``gamma``, ``delta``
qper_qpar ``qper``, ``qpar``          qper_qpar                        ``gamma``, ``delta``                                          ``gamma``, ``delta``                                  ``x``, ``y``, ``z``
tth2      ``tth``, ``alpha``          tth2                             ``gamma``, ``delta``                                          ``gamma``, ``delta``
========= =========================== ================================ ============================================================= ===================================================== ===============================================

.. index:: SOLEIL_SIRIUS_TURRET, geometry; SOLEIL_SIRIUS_TURRET

.. _SOLEIL_SIRIUS_TURRET_table:

Geometry: ``SOLEIL SIRIUS TURRET``
++++++++++++++++++++++++++++++++++

* real axes: ``basepitch``, ``thetah``, ``alphay``, ``alphax``, ``delta``, ``gamma``
* pseudo axes: depends on the engine

========= ========================== ======================= ======================================================================= ================================ ===================
engine    pseudo axes                mode                    axes read                                                               axes written                     extra parameters
========= ========================== ======================= ======================================================================= ================================ ===================
emergence ``emergence``, ``azimuth`` emergence               ``basepitch``, ``thetah``, ``alphay``, ``alphax``, ``delta``, ``gamma``                                  ``x``, ``y``, ``z``
hkl       ``h``, ``k``, ``l``        lifting_detector_thetah ``basepitch``, ``thetah``, ``alphay``, ``alphax``, ``delta``, ``gamma`` ``thetah``, ``delta``, ``gamma``
incidence ``incidence``, ``azimuth`` incidence               ``basepitch``, ``thetah``, ``alphay``, ``alphax``                                                        ``x``, ``y``, ``z``
q2        ``q``, ``alpha``           q2                      ``gamma``, ``delta``                                                    ``gamma``, ``delta``
qper_qpar ``qper``, ``qpar``         qper_qpar               ``gamma``, ``delta``                                                    ``gamma``, ``delta``             ``x``, ``y``, ``z``
tth2      ``tth``, ``alpha``         tth2                    ``gamma``, ``delta``                                                    ``gamma``, ``delta``
========= ========================== ======================= ======================================================================= ================================ ===================

.. index:: SOLEIL_SIXS_MED1+2, geometry; SOLEIL_SIXS_MED1+2

.. _SOLEIL_SIXS_MED1+2_table:

Geometry: ``SOLEIL SIXS MED1+2``
++++++++++++++++++++++++++++++++

* real axes: ``pitch``, ``mu``, ``gamma``, ``delta``
* pseudo axes: depends on the engine

========= ========================== =========== ======================================= ============================ ===================
engine    pseudo axes                mode        axes read                               axes written                 extra parameters
========= ========================== =========== ======================================= ============================ ===================
emergence ``emergence``, ``azimuth`` emergence   ``pitch``, ``mu``, ``gamma``, ``delta``                              ``x``, ``y``, ``z``
hkl       ``h``, ``k``, ``l``        delta_fixed ``pitch``, ``mu``, ``gamma``, ``delta`` ``pitch``, ``mu``, ``gamma``
hkl       ``h``, ``k``, ``l``        pitch_fixed ``pitch``, ``mu``, ``gamma``, ``delta`` ``mu``, ``gamma``, ``delta``
incidence ``incidence``, ``azimuth`` incidence   ``pitch``, ``mu``                                                    ``x``, ``y``, ``z``
q2        ``q``, ``alpha``           q2          ``gamma``, ``delta``                    ``gamma``, ``delta``
qper_qpar ``qper``, ``qpar``         qper_qpar   ``gamma``, ``delta``                    ``gamma``, ``delta``         ``x``, ``y``, ``z``
tth2      ``tth``, ``alpha``         tth2        ``gamma``, ``delta``                    ``gamma``, ``delta``
========= ========================== =========== ======================================= ============================ ===================

.. index:: SOLEIL_SIXS_MED2+2, geometry; SOLEIL_SIXS_MED2+2

.. _SOLEIL_SIXS_MED2+2_table:

Geometry: ``SOLEIL SIXS MED2+2``
++++++++++++++++++++++++++++++++

* real axes: ``beta``, ``mu``, ``omega``, ``gamma``, ``delta``
* pseudo axes: depends on the engine

========= ========================== =============== ================================================= ======================================= ==================================
engine    pseudo axes                mode            axes read                                         axes written                            extra parameters
========= ========================== =============== ================================================= ======================================= ==================================
emergence ``emergence``, ``azimuth`` emergence       ``beta``, ``mu``, ``omega``, ``gamma``, ``delta``                                         ``x``, ``y``, ``z``
hkl       ``h``, ``k``, ``l``        emergence_fixed ``beta``, ``mu``, ``omega``, ``gamma``, ``delta`` ``mu``, ``omega``, ``gamma``, ``delta`` ``x``, ``y``, ``z``, ``emergence``
hkl       ``h``, ``k``, ``l``        mu_fixed        ``beta``, ``mu``, ``omega``, ``gamma``, ``delta`` ``omega``, ``gamma``, ``delta``
hkl       ``h``, ``k``, ``l``        reflectivity    ``beta``, ``mu``, ``omega``, ``gamma``, ``delta`` ``mu``, ``omega``, ``gamma``, ``delta``
incidence ``incidence``, ``azimuth`` incidence       ``beta``, ``mu``, ``omega``                                                               ``x``, ``y``, ``z``
q2        ``q``, ``alpha``           q2              ``gamma``, ``delta``                              ``gamma``, ``delta``
qper_qpar ``qper``, ``qpar``         qper_qpar       ``gamma``, ``delta``                              ``gamma``, ``delta``                    ``x``, ``y``, ``z``
tth2      ``tth``, ``alpha``         tth2            ``gamma``, ``delta``                              ``gamma``, ``delta``
========= ========================== =============== ================================================= ======================================= ==================================

.. index:: SOLEIL_SIXS_MED2+3, geometry; SOLEIL_SIXS_MED2+3

.. _SOLEIL_SIXS_MED2+3_table:

Geometry: ``SOLEIL SIXS MED2+3``
++++++++++++++++++++++++++++++++

* real axes: ``beta``, ``mu``, ``omega``, ``gamma``, ``delta``, ``eta_a``
* pseudo axes: depends on the engine

========= ========================== =============== ============================================================ ======================================= ==================================
engine    pseudo axes                mode            axes read                                                    axes written                            extra parameters
========= ========================== =============== ============================================================ ======================================= ==================================
emergence ``emergence``, ``azimuth`` emergence       ``beta``, ``mu``, ``omega``, ``gamma``, ``delta``                                                    ``x``, ``y``, ``z``
hkl       ``h``, ``k``, ``l``        emergence_fixed ``beta``, ``mu``, ``omega``, ``gamma``, ``delta``, ``eta_a`` ``mu``, ``omega``, ``gamma``, ``delta`` ``x``, ``y``, ``z``, ``emergence``
hkl       ``h``, ``k``, ``l``        gamma_fixed     ``beta``, ``mu``, ``omega``, ``gamma``, ``delta``, ``eta_a`` ``mu``, ``omega``, ``delta``
hkl       ``h``, ``k``, ``l``        mu_fixed        ``beta``, ``mu``, ``omega``, ``gamma``, ``delta``, ``eta_a`` ``omega``, ``gamma``, ``delta``
incidence ``incidence``, ``azimuth`` incidence       ``beta``, ``mu``, ``omega``                                                                          ``x``, ``y``, ``z``
q2        ``q``, ``alpha``           q2              ``gamma``, ``delta``                                         ``gamma``, ``delta``
qper_qpar ``qper``, ``qpar``         qper_qpar       ``gamma``, ``delta``                                         ``gamma``, ``delta``                    ``x``, ``y``, ``z``
tth2      ``tth``, ``alpha``         tth2            ``gamma``, ``delta``                                         ``gamma``, ``delta``
========= ========================== =============== ============================================================ ======================================= ==================================

.. index:: SOLEIL_SIXS_MED2+3_v2, geometry; SOLEIL_SIXS_MED2+3_v2

.. _SOLEIL_SIXS_MED2+3_v2_table:

Geometry: ``SOLEIL SIXS MED2+3 v2``
+++++++++++++++++++++++++++++++++++

* real axes: ``mu``, ``omega``, ``gamma``, ``delta``, ``eta_a``
* pseudo axes: depends on the engine

========= ========================== =============== ================================================== ======================================= ==================================
engine    pseudo axes                mode            axes read                                          axes written                            extra parameters
========= ========================== =============== ================================================== ======================================= ==================================
emergence ``emergence``, ``azimuth`` emergence       ``beta``, ``mu``, ``omega``, ``gamma``, ``delta``                                          ``x``, ``y``, ``z``
hkl       ``h``, ``k``, ``l``        emergence_fixed ``mu``, ``omega``, ``gamma``, ``delta``, ``eta_a`` ``mu``, ``omega``, ``gamma``, ``delta`` ``x``, ``y``, ``z``, ``emergence``
hkl       ``h``, ``k``, ``l``        gamma_fixed     ``mu``, ``omega``, ``gamma``, ``delta``, ``eta_a`` ``mu``, ``omega``, ``delta``
hkl       ``h``, ``k``, ``l``        mu_fixed        ``mu``, ``omega``, ``gamma``, ``delta``, ``eta_a`` ``omega``, ``gamma``, ``delta``
incidence ``incidence``, ``azimuth`` incidence       ``beta``, ``mu``, ``omega``                                                                ``x``, ``y``, ``z``
q2        ``q``, ``alpha``           q2              ``gamma``, ``delta``                               ``gamma``, ``delta``
qper_qpar ``qper``, ``qpar``         qper_qpar       ``gamma``, ``delta``                               ``gamma``, ``delta``                    ``x``, ``y``, ``z``
tth2      ``tth``, ``alpha``         tth2            ``gamma``, ``delta``                               ``gamma``, ``delta``
========= ========================== =============== ================================================== ======================================= ==================================

.. index:: ZAXIS, geometry; ZAXIS

.. _ZAXIS_table:

Geometry: ``ZAXIS``
+++++++++++++++++++

* real axes: ``mu``, ``omega``, ``delta``, ``gamma``
* pseudo axes: depends on the engine

========= ========================== ============ ======================================= ======================================= ===================
engine    pseudo axes                mode         axes read                               axes written                            extra parameters
========= ========================== ============ ======================================= ======================================= ===================
emergence ``emergence``, ``azimuth`` emergence    ``mu``, ``omega``, ``delta``, ``gamma``                                         ``x``, ``y``, ``z``
hkl       ``h``, ``k``, ``l``        reflectivity ``mu``, ``omega``, ``delta``, ``gamma`` ``mu``, ``omega``, ``delta``, ``gamma``
hkl       ``h``, ``k``, ``l``        zaxis        ``mu``, ``omega``, ``delta``, ``gamma`` ``omega``, ``delta``, ``gamma``
incidence ``incidence``, ``azimuth`` incidence    ``mu``, ``omega``                                                               ``x``, ``y``, ``z``
q2        ``q``, ``alpha``           q2           ``gamma``, ``delta``                    ``gamma``, ``delta``
qper_qpar ``qper``, ``qpar``         qper_qpar    ``gamma``, ``delta``                    ``gamma``, ``delta``                    ``x``, ``y``, ``z``
tth2      ``tth``, ``alpha``         tth2         ``gamma``, ``delta``                    ``gamma``, ``delta``
========= ========================== ============ ======================================= ======================================= ===================
