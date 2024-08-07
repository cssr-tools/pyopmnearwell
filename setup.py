"""pyopmnearwell: A framework to simulate near well dynamics using OPM Flow"""

from setuptools import find_packages, setup

setup(
    package_dir={"": "src"},
    package_data={find_packages(where="src")[0]: ["py.typed"]},
    packages=find_packages(where="src"),
)
