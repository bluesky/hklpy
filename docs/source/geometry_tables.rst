.. geometry_tables:

=================================
Tables of Diffractometer Geometry
=================================

Tables are provided for the different geometries and then, for each
geometry, the calculation engines, pseudo axes required, modes of
operation, and any additional parameters required by the mode.

Geometries indexed by number of circles
---------------------------------------

The different diffractometer geometries are distinguished, primarily, by
the number of axes (circles) and the names of each.  This table is
sorted first by the number of circles, and then the geometry name (as
used here in *hklpy*).

======== ==================================================== =======================================================================
#circles geometry                                             real_axes
======== ==================================================== =======================================================================
4        :ref:`E4CH <E4CH_table>`                             ``omega``, ``chi``, ``phi``, ``tth``
4        :ref:`E4CV <E4CV_table>`                             ``omega``, ``chi``, ``phi``, ``tth``
4        :ref:`K4CV <K4CV_table>`                             ``komega``, ``kappa``, ``kphi``, ``tth``
4        :ref:`SoleilMars <SoleilMars_table>`                 ``omega``, ``chi``, ``phi``, ``tth``
4        :ref:`SoleilSixsMed1p2 <SoleilSixsMed1p2_table>`     ``pitch``, ``mu``, ``gamma``, ``delta``
4        :ref:`Zaxis <Zaxis_table>`                           ``mu``, ``omega``, ``delta``, ``gamma``
5        :ref:`SoleilSixsMed2p2 <SoleilSixsMed2p2_table>`     ``beta``, ``mu``, ``omega``, ``gamma``, ``delta``
6        :ref:`E6C <E6C_table>`                               ``mu``, ``omega``, ``chi``, ``phi``, ``gamma``, ``delta``
6        :ref:`K6C <K6C_table>`                               ``mu``, ``komega``, ``kappa``, ``kphi``, ``gamma``, ``delta``
6        :ref:`Petra3_p09_eh2 <Petra3_p09_eh2_table>`         ``mu``, ``omega``, ``chi``, ``phi``, ``delta``, ``gamma``
6        :ref:`SoleilSiriusKappa <SoleilSiriusKappa_table>`   ``mu``, ``komega``, ``kappa``, ``kphi``, ``delta``, ``gamma``
6        :ref:`SoleilSiriusTurret <SoleilSiriusTurret_table>` ``basepitch``, ``thetah``, ``alphay``, ``alphax``, ``delta``, ``gamma``
6        :ref:`SoleilSixsMed2p3 <SoleilSixsMed2p3_table>`     ``beta``, ``mu``, ``omega``, ``gamma``, ``delta``, ``eta_a``
======== ==================================================== =======================================================================

Tables for each geometry
------------------------

A table is provided for each diffractometer geometry listing the
calculation engines, pseudo axes required, modes of operation, and any
additional parameters required by the mode.

.. index:: E4CH, geometry; E4CH

.. _E4CH_table:

Geometry: `E4CH`
++++++++++++++++

real axes: ``omega``, ``chi``, ``phi``, ``tth``

========= ========================== ================== ===============================
engine    pseudo_axes                mode               parameters
========= ========================== ================== ===============================
hkl       ``h``, ``k``, ``l``        bissector
hkl       ``h``, ``k``, ``l``        constant_omega
hkl       ``h``, ``k``, ``l``        constant_chi
hkl       ``h``, ``k``, ``l``        constant_phi
hkl       ``h``, ``k``, ``l``        double_diffraction ``h2``, ``k2``, ``l2``
hkl       ``h``, ``k``, ``l``        psi_constant       ``h2``, ``k2``, ``l2``, ``psi``
psi       ``psi``                    psi                ``h2``, ``k2``, ``l2``
q         ``q``                      q
incidence ``incidence``, ``azimuth`` incidence          ``x``, ``y``, ``z``
emergence ``emergence``, ``azimuth`` emergence          ``x``, ``y``, ``z``
========= ========================== ================== ===============================

.. index:: E4CV, geometry; E4CV

.. _E4CV_table:

Geometry: `E4CV`
++++++++++++++++

real axes: ``omega``, ``chi``, ``phi``, ``tth``

========= ========================== ================== ===============================
engine    pseudo_axes                mode               parameters
========= ========================== ================== ===============================
hkl       ``h``, ``k``, ``l``        bissector
hkl       ``h``, ``k``, ``l``        constant_omega
hkl       ``h``, ``k``, ``l``        constant_chi
hkl       ``h``, ``k``, ``l``        constant_phi
hkl       ``h``, ``k``, ``l``        double_diffraction ``h2``, ``k2``, ``l2``
hkl       ``h``, ``k``, ``l``        psi_constant       ``h2``, ``k2``, ``l2``, ``psi``
psi       ``psi``                    psi                ``h2``, ``k2``, ``l2``
q         ``q``                      q
incidence ``incidence``, ``azimuth`` incidence          ``x``, ``y``, ``z``
========= ========================== ================== ===============================

.. index:: E6C, geometry; E6C

.. _E6C_table:

Geometry: `E6C`
+++++++++++++++

real axes: ``mu``, ``omega``, ``chi``, ``phi``, ``gamma``, ``delta``

========= ========================== ============================= ===============================
engine    pseudo_axes                mode                          parameters
========= ========================== ============================= ===============================
hkl       ``h``, ``k``, ``l``        bissector_vertical
hkl       ``h``, ``k``, ``l``        constant_omega_vertical
hkl       ``h``, ``k``, ``l``        constant_chi_vertical
hkl       ``h``, ``k``, ``l``        constant_phi_vertical
hkl       ``h``, ``k``, ``l``        lifting_detector_phi
hkl       ``h``, ``k``, ``l``        lifting_detector_omega
hkl       ``h``, ``k``, ``l``        lifting_detector_mu
hkl       ``h``, ``k``, ``l``        double_diffraction_vertical   ``h2``, ``k2``, ``l2``
hkl       ``h``, ``k``, ``l``        bissector_horizontal
hkl       ``h``, ``k``, ``l``        double_diffraction_horizontal ``h2``, ``k2``, ``l2``
hkl       ``h``, ``k``, ``l``        psi_constant_vertical         ``h2``, ``k2``, ``l2``, ``psi``
hkl       ``h``, ``k``, ``l``        psi_constant_horizontal       ``h2``, ``k2``, ``l2``, ``psi``
hkl       ``h``, ``k``, ``l``        constant_mu_horizontal
psi       ``psi``                    psi_vertical                  ``h2``, ``k2``, ``l2``
q2        ``q``, ``alpha``           q2
qper_qpar ``qper``, ``qpar``         qper_qpar                     ``x``, ``y``, ``z``
tth2      ``tth``, ``alpha``         tth2
incidence ``incidence``, ``azimuth`` incidence                     ``x``, ``y``, ``z``
emergence ``emergence``, ``azimuth`` emergence                     ``x``, ``y``, ``z``
========= ========================== ============================= ===============================

.. index:: K4CV, geometry; K4CV

.. _K4CV_table:

Geometry: `K4CV`
++++++++++++++++

real axes: ``komega``, ``kappa``, ``kphi``, ``tth``

========= =========================== ================== ===============================
engine    pseudo_axes                 mode               parameters
========= =========================== ================== ===============================
hkl       ``h``, ``k``, ``l``         bissector
hkl       ``h``, ``k``, ``l``         constant_omega     ``omega``
hkl       ``h``, ``k``, ``l``         constant_chi       ``chi``
hkl       ``h``, ``k``, ``l``         constant_phi       ``phi``
hkl       ``h``, ``k``, ``l``         double_diffraction ``h2``, ``k2``, ``l2``
hkl       ``h``, ``k``, ``l``         psi_constant       ``h2``, ``k2``, ``l2``, ``psi``
eulerians ``omega``, ``chi``, ``phi`` eulerians          ``solutions``
psi       ``psi``                     psi                ``h2``, ``k2``, ``l2``
q         ``q``                       q
incidence ``incidence``, ``azimuth``  incidence          ``x``, ``y``, ``z``
emergence ``emergence``, ``azimuth``  emergence          ``x``, ``y``, ``z``
========= =========================== ================== ===============================

.. index:: K6C, geometry; K6C

.. _K6C_table:

Geometry: `K6C`
+++++++++++++++

real axes: ``mu``, ``komega``, ``kappa``, ``kphi``, ``gamma``, ``delta``

========= =========================== ============================= ===============================================
engine    pseudo_axes                 mode                          parameters
========= =========================== ============================= ===============================================
hkl       ``h``, ``k``, ``l``         bissector_vertical
hkl       ``h``, ``k``, ``l``         constant_omega_vertical       ``omega``
hkl       ``h``, ``k``, ``l``         constant_chi_vertical         ``chi``
hkl       ``h``, ``k``, ``l``         constant_phi_vertical         ``phi``
hkl       ``h``, ``k``, ``l``         lifting_detector_kphi
hkl       ``h``, ``k``, ``l``         lifting_detector_komega
hkl       ``h``, ``k``, ``l``         lifting_detector_mu
hkl       ``h``, ``k``, ``l``         double_diffraction_vertical   ``h2``, ``k2``, ``l2``
hkl       ``h``, ``k``, ``l``         bissector_horizontal
hkl       ``h``, ``k``, ``l``         constant_phi_horizontal       ``phi``
hkl       ``h``, ``k``, ``l``         constant_kphi_horizontal
hkl       ``h``, ``k``, ``l``         double_diffraction_horizontal ``h2``, ``k2``, ``l2``
hkl       ``h``, ``k``, ``l``         psi_constant_vertical         ``h2``, ``k2``, ``l2``, ``psi``
hkl       ``h``, ``k``, ``l``         constant_incidence            ``x``, ``y``, ``z``, ``incidence``, ``azimuth``
eulerians ``omega``, ``chi``, ``phi`` eulerians                     ``solutions``
psi       ``psi``                     psi_vertical                  ``h2``, ``k2``, ``l2``
q2        ``q``, ``alpha``            q2
qper_qpar ``qper``, ``qpar``          qper_qpar                     ``x``, ``y``, ``z``
incidence ``incidence``, ``azimuth``  incidence                     ``x``, ``y``, ``z``
tth2      ``tth``, ``alpha``          tth2
emergence ``emergence``, ``azimuth``  emergence                     ``x``, ``y``, ``z``
========= =========================== ============================= ===============================================

.. index:: Petra3_p09_eh2, geometry; Petra3_p09_eh2

.. _Petra3_p09_eh2_table:

Geometry: `Petra3_p09_eh2`
++++++++++++++++++++++++++

real axes: ``mu``, ``omega``, ``chi``, ``phi``, ``delta``, ``gamma``

====== =================== =================================== ==========
engine pseudo_axes         mode                                parameters
====== =================== =================================== ==========
hkl    ``h``, ``k``, ``l`` zaxis + alpha-fixed
hkl    ``h``, ``k``, ``l`` zaxis + beta-fixed
hkl    ``h``, ``k``, ``l`` zaxis + alpha=beta
hkl    ``h``, ``k``, ``l`` 4-circles bissecting horizontal
hkl    ``h``, ``k``, ``l`` 4-circles constant omega horizontal
hkl    ``h``, ``k``, ``l`` 4-circles constant chi horizontal
hkl    ``h``, ``k``, ``l`` 4-circles constant phi horizontal
hkl    ``h``, ``k``, ``l`` lifting detector mu
hkl    ``h``, ``k``, ``l`` lifting detector omega
hkl    ``h``, ``k``, ``l`` lifting detector chi
hkl    ``h``, ``k``, ``l`` lifting detector phi
====== =================== =================================== ==========

.. index:: SoleilMars, geometry; SoleilMars

.. _SoleilMars_table:

Geometry: `SoleilMars`
++++++++++++++++++++++

real axes: ``omega``, ``chi``, ``phi``, ``tth``

========= ========================== ================== ===============================
engine    pseudo_axes                mode               parameters
========= ========================== ================== ===============================
hkl       ``h``, ``k``, ``l``        bissector
hkl       ``h``, ``k``, ``l``        constant_omega
hkl       ``h``, ``k``, ``l``        constant_chi
hkl       ``h``, ``k``, ``l``        constant_phi
hkl       ``h``, ``k``, ``l``        double_diffraction ``h2``, ``k2``, ``l2``
hkl       ``h``, ``k``, ``l``        psi_constant       ``h2``, ``k2``, ``l2``, ``psi``
psi       ``psi``                    psi                ``h2``, ``k2``, ``l2``
q         ``q``                      q
incidence ``incidence``, ``azimuth`` incidence          ``x``, ``y``, ``z``
========= ========================== ================== ===============================

.. index:: SoleilSiriusKappa, geometry; SoleilSiriusKappa

.. _SoleilSiriusKappa_table:

Geometry: `SoleilSiriusKappa`
+++++++++++++++++++++++++++++

real axes: ``mu``, ``komega``, ``kappa``, ``kphi``, ``delta``, ``gamma``

========= =========================== ================================ ===============================================
engine    pseudo_axes                 mode                             parameters
========= =========================== ================================ ===============================================
hkl       ``h``, ``k``, ``l``         bissector_vertical
hkl       ``h``, ``k``, ``l``         constant_omega_vertical          ``omega``
hkl       ``h``, ``k``, ``l``         constant_chi_vertical            ``chi``
hkl       ``h``, ``k``, ``l``         constant_phi_vertical            ``phi``
hkl       ``h``, ``k``, ``l``         lifting_detector_kphi
hkl       ``h``, ``k``, ``l``         lifting_detector_komega
hkl       ``h``, ``k``, ``l``         lifting_detector_mu
hkl       ``h``, ``k``, ``l``         double_diffraction_vertical      ``h2``, ``k2``, ``l2``
hkl       ``h``, ``k``, ``l``         bissector_horizontal
hkl       ``h``, ``k``, ``l``         constant_phi_horizontal          ``phi``
hkl       ``h``, ``k``, ``l``         constant_kphi_horizontal
hkl       ``h``, ``k``, ``l``         double_diffraction_horizontal    ``h2``, ``k2``, ``l2``
hkl       ``h``, ``k``, ``l``         psi_constant_vertical            ``h2``, ``k2``, ``l2``, ``psi``
hkl       ``h``, ``k``, ``l``         constant_incidence               ``x``, ``y``, ``z``, ``incidence``, ``azimuth``
eulerians ``omega``, ``chi``, ``phi`` eulerians                        ``solutions``
psi       ``psi``                     psi_vertical_soleil_sirius_kappa ``h2``, ``k2``, ``l2``
q2        ``q``, ``alpha``            q2
qper_qpar ``qper``, ``qpar``          qper_qpar                        ``x``, ``y``, ``z``
tth2      ``tth``, ``alpha``          tth2
incidence ``incidence``, ``azimuth``  incidence                        ``x``, ``y``, ``z``
emergence ``emergence``, ``azimuth``  emergence                        ``x``, ``y``, ``z``
========= =========================== ================================ ===============================================

.. index:: SoleilSiriusTurret, geometry; SoleilSiriusTurret

.. _SoleilSiriusTurret_table:

Geometry: `SoleilSiriusTurret`
++++++++++++++++++++++++++++++

real axes: ``basepitch``, ``thetah``, ``alphay``, ``alphax``, ``delta``, ``gamma``

========= ========================== ======================= ===================
engine    pseudo_axes                mode                    parameters
========= ========================== ======================= ===================
hkl       ``h``, ``k``, ``l``        lifting_detector_thetah
q2        ``q``, ``alpha``           q2
qper_qpar ``qper``, ``qpar``         qper_qpar               ``x``, ``y``, ``z``
tth2      ``tth``, ``alpha``         tth2
incidence ``incidence``, ``azimuth`` incidence               ``x``, ``y``, ``z``
emergence ``emergence``, ``azimuth`` emergence               ``x``, ``y``, ``z``
========= ========================== ======================= ===================

.. index:: SoleilSixsMed1p2, geometry; SoleilSixsMed1p2

.. _SoleilSixsMed1p2_table:

Geometry: `SoleilSixsMed1p2`
++++++++++++++++++++++++++++

real axes: ``pitch``, ``mu``, ``gamma``, ``delta``

========= ========================== =========== ===================
engine    pseudo_axes                mode        parameters
========= ========================== =========== ===================
hkl       ``h``, ``k``, ``l``        pitch_fixed
hkl       ``h``, ``k``, ``l``        delta_fixed
q2        ``q``, ``alpha``           q2
qper_qpar ``qper``, ``qpar``         qper_qpar   ``x``, ``y``, ``z``
tth2      ``tth``, ``alpha``         tth2
incidence ``incidence``, ``azimuth`` incidence   ``x``, ``y``, ``z``
emergence ``emergence``, ``azimuth`` emergence   ``x``, ``y``, ``z``
========= ========================== =========== ===================

.. index:: SoleilSixsMed2p2, geometry; SoleilSixsMed2p2

.. _SoleilSixsMed2p2_table:

Geometry: `SoleilSixsMed2p2`
++++++++++++++++++++++++++++

real axes: ``beta``, ``mu``, ``omega``, ``gamma``, ``delta``

========= ========================== =============== ==================================
engine    pseudo_axes                mode            parameters
========= ========================== =============== ==================================
hkl       ``h``, ``k``, ``l``        mu_fixed
hkl       ``h``, ``k``, ``l``        reflectivity
hkl       ``h``, ``k``, ``l``        emergence_fixed ``x``, ``y``, ``z``, ``emergence``
q2        ``q``, ``alpha``           q2
qper_qpar ``qper``, ``qpar``         qper_qpar       ``x``, ``y``, ``z``
tth2      ``tth``, ``alpha``         tth2
incidence ``incidence``, ``azimuth`` incidence       ``x``, ``y``, ``z``
emergence ``emergence``, ``azimuth`` emergence       ``x``, ``y``, ``z``
========= ========================== =============== ==================================

.. index:: SoleilSixsMed2p3, geometry; SoleilSixsMed2p3

.. _SoleilSixsMed2p3_table:

Geometry: `SoleilSixsMed2p3`
++++++++++++++++++++++++++++

real axes: ``beta``, ``mu``, ``omega``, ``gamma``, ``delta``, ``eta_a``

========= ========================== =============== ==================================
engine    pseudo_axes                mode            parameters
========= ========================== =============== ==================================
hkl       ``h``, ``k``, ``l``        mu_fixed
hkl       ``h``, ``k``, ``l``        gamma_fixed
hkl       ``h``, ``k``, ``l``        emergence_fixed ``x``, ``y``, ``z``, ``emergence``
q2        ``q``, ``alpha``           q2
qper_qpar ``qper``, ``qpar``         qper_qpar       ``x``, ``y``, ``z``
tth2      ``tth``, ``alpha``         tth2
incidence ``incidence``, ``azimuth`` incidence       ``x``, ``y``, ``z``
emergence ``emergence``, ``azimuth`` emergence       ``x``, ``y``, ``z``
========= ========================== =============== ==================================

.. index:: Zaxis, geometry; Zaxis

.. _Zaxis_table:

Geometry: `Zaxis`
+++++++++++++++++

real axes: ``mu``, ``omega``, ``delta``, ``gamma``

========= ========================== ============ ===================
engine    pseudo_axes                mode         parameters
========= ========================== ============ ===================
hkl       ``h``, ``k``, ``l``        zaxis
hkl       ``h``, ``k``, ``l``        reflectivity
q2        ``q``, ``alpha``           q2
qper_qpar ``qper``, ``qpar``         qper_qpar    ``x``, ``y``, ``z``
tth2      ``tth``, ``alpha``         tth2
incidence ``incidence``, ``azimuth`` incidence    ``x``, ``y``, ``z``
emergence ``emergence``, ``azimuth`` emergence    ``x``, ``y``, ``z``
========= ========================== ============ ===================
