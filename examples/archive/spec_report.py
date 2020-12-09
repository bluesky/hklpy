#!/usr/bin/env python

"""
Report the diffractometer structure of SPEC data files
"""

import os
import pyRestTable
from spec2nexus.spec import SpecDataFile


SUBDIR = os.path.join(os.path.dirname(__file__), "hkl_data")
SUBDIR = os.path.join("/tmp", "spec_data")


def show_ref(refl):
    s = (
        f" {refl.h:.2f}"
        f" {refl.k:.2f}"
        f" {refl.l:.2f}"
    )
    s = f"({s.strip()}) "
    s += f" wavelength={refl.wavelength:.4f}"
    for k, v in refl.angles.items():
        s += f" {k}={v:.4f}"
    return s


def show_UB(ub):
    s = []
    for row in ub:
        r = [
            f"{v:2.4f}"
            for v in row
        ]
        s.append("   ".join(r))
    return "\n".join(s)


def report(specfile):
    specfile = SpecDataFile(specfile)

    # search for scans with hkl in the name
    hklscans = [
        specscan
        for specscan in specfile.getScanCommands()
        if specscan.find("hkl") > 0
    ]
    if len(hklscans):
        scan_number = int(hklscans[0].split()[1])
    else:
        scan_number = specfile.getLastScanNumber()

    specscan = specfile.getScan(scan_number)

    spec_d = specscan.diffractometer
    spec_d.UB = spec_d.geometry_parameters["ub_matrix"][2]

    terms = {
        "SPEC file": specfile.specFile,
        "scan #": specscan.scanNum,
        "SPEC scanCmd": specscan.scanCmd,
        "geometry": spec_d.geometry_name,
        "mode": spec_d.mode,
        "lattice": spec_d.lattice,
        "wavelength": spec_d.wavelength,
        "reflection 1": show_ref(spec_d.reflections[0]),
        "reflection 2": show_ref(spec_d.reflections[1]),
        "[UB]": show_UB(spec_d.UB),
    }
    tbl = pyRestTable.Table()
    tbl.labels = "term value".split()
    for k, v in terms.items():
        tbl.addRow((k, v))
    print(tbl)


def main():
    for item in sorted(os.listdir(SUBDIR)):
        print(item, "\n" + "="*40)
        try:
            report(os.path.join(SUBDIR, item))
        except Exception as exc:
            print(item, exc)
        print("")


if __name__ == "__main__":
    main()
