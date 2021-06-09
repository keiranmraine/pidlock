#!/usr/bin/env python
from setuptools import setup, find_packages
from codecs import open
from os import path

VERSION = "v3.0.1"

here = path.abspath(path.dirname(__file__))

# Get requirements from requirements.txt file
with open(path.join(here, "requirements.txt"), encoding="utf-8") as f:
    requirements = f.read().splitlines()

# Get the long description from the README file
with open(path.join(here, "README.md"), encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="pidlock",
    version=VERSION,
    description="Simple PID based locking for cronjobs, UNIX scripts or python programs",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/keiranmraine/pidlock",
    download_url="https://github.com/keiranmraine/pidlock/archive/{}.tar.gz".format(
        VERSION
    ),
    author="Keiran Raine",
    author_email="keiranmraine@gmail.com",
    license="MIT",
    py_modules=["pidlock"],
    classifiers=[
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Intended Audience :: Information Technology",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.2",
        "Programming Language :: Python :: 3.3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Topic :: Utilities",
        "Operating System :: MacOS",
        "Operating System :: POSIX",
    ],
    keywords="PID Based File Locking",
    packages=find_packages(exclude=["contrib", "docs", "tests"]),
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "pidlock = pidlock:pidlock_cli",
        ]
    },
)
