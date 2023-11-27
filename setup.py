"""pyopmnearwell: A framework to simulate near well dynamics using OPM Flow"""

from setuptools import find_packages, setup

with open("README.md", "r", encoding="utf8") as file:
    long_description = file.read()

with open("requirements.txt", "r", encoding="utf8") as file:
    install_requires = file.read().splitlines()

with open("dev-requirements.txt", "r", encoding="utf8") as file:
    dev_requires = file.read().splitlines()

setup(
    name="pyopmnearwell",
    version="2023.10",
    install_requires=install_requires,
    extras_require={"dev": dev_requires},
    setup_requires=["setuptools_scm"],
    description="A framework to simulate near well dynamics using OPM Flow",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/dmar/pyopmnearwell",
    author="David Landa-Marbán, Peter Moritz von Schultzendorff",
    mantainer="David Landa-Marbán, Peter Moritz von Schultzendorff",
    mantainer_email="dmar@norceresearch.no",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Science/Research",
        "Natural Language :: English",
        "Topic :: Scientific/Engineering",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    keywords="co2 dynamics hydrogen opm wells saltprecipitation",
    package_dir={"": "src"},
    package_data={find_packages(where="src")[0]: ["py.typed"]},
    packages=find_packages(where="src"),
    license="GPL-3.0",
    python_requires=">=3.8, <4",
    entry_points={
        "console_scripts": [
            "pyopmnearwell=pyopmnearwell.core.pyopmnearwell:main",
        ]
    },
    include_package_data=True,
)
