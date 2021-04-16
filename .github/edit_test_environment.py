#!/usr/bin/env python

"""
modify the environment.yml file

USAGE::

    python edit_test_environment.py ${ENV_NAME}
"""

import os
import sys
import yaml

PATH = os.path.join(os.path.dirname(__file__), "..")
CONFIG_FILE = os.path.join(PATH, "environment.yml")


def main():
    # get command-line argument(s)
    env_name = sys.argv[1]  # hklpy-test-${{ matrix.python-version }}

    # read the environment file
    with open(CONFIG_FILE, "r") as f:
        full_config = yaml.load(f, Loader=yaml.FullLoader)

    # set the specific environment name
    full_config["name"] = env_name

    # Extract the pip requirements
    pip_requirements = full_config["dependencies"][-1]["pip"]
    # remove them from the conda environment
    full_config["dependencies"] = full_config["dependencies"][:-1]

    # write a new environment YAML file without the pip requirements
    with open(os.path.join(PATH, "conda_env.yml"), "w") as f:
        yaml.dump(full_config, f)

    # write the  pip requirements file
    with open(os.path.join(PATH, "pip_req.txt"), "w") as f:
        f.write("\n".join(pip_requirements))


if __name__ == "__main__":
    main()
