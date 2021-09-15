#!/usr/bin/env python
from setuptools import setup, find_packages
import versioneer


desc = "Controls for using diffractometers within the Bluesky Framework"
desc += ": https://blueskyproject.io"
with open("README.md", "r") as f:
    long_desc = f.read()

setup(
    name="hklpy",
    version=versioneer.get_version(),
    cmdclass=versioneer.get_cmdclass(),
    description=desc,
    long_description=long_desc,
    long_description_content_type="text/markdown",
    maintainer="prjemian",
    maintainer_email="prjemian+hklpy@gmail.com",
    url="https://github.com/bluesky/hklpy",
    license="BSD",
    packages=find_packages(),
)
