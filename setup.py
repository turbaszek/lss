import os

from setuptools import find_packages, setup

VERSION = "1.0.0dev"

BASE_PATH = os.path.dirname(os.path.realpath(__file__))

DEVEL_REQUIREMENTS = [
    "black==20.8b1",
    "pre-commit==2.7.1",
    "pytest==6.1.1",
]

INSTALL_REQUIREMENTS = ["python-rtmidi>=1.4.9", "mido>=1.2.10", "click>=7.1.2"]
EXTRAS_REQUIREMENTS = {"devel": DEVEL_REQUIREMENTS}


def get_long_description() -> str:
    try:
        with open(os.path.join(BASE_PATH, "README.md")) as file:
            description = file.read()
    except FileNotFoundError:
        description = ""
    return description


def do_setup() -> None:
    setup(
        name="lss",
        description="Step sequencer based on Novation Launchpad",
        long_description=get_long_description(),
        long_description_content_type="text/markdown",
        license="Apache License 2.0",
        version=VERSION,
        packages=find_packages(include=["lss*"]),
        package_data={"lss": ["py.typed"]},
        include_package_data=True,
        zip_safe=False,
        entry_points={"console_scripts": ["lss = lss.__main__:main"]},
        install_requires=INSTALL_REQUIREMENTS,
        setup_requires=["docutils", "gitpython", "setuptools", "wheel"],
        extras_require=EXTRAS_REQUIREMENTS,
        classifiers=[
            "Environment :: Console",
            "License :: OSI Approved :: Apache Software License",
            "Programming Language :: Python :: 3.8",
        ],
        python_requires="~=3.8",
    )


if __name__ == "__main__":
    do_setup()
