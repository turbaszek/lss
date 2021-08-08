import os

from setuptools import find_packages, setup

VERSION = "1.0.0dev"

BASE_PATH = os.path.dirname(os.path.realpath(__file__))

DEVEL_REQUIREMENTS = [
    "black==20.8b1",
    "pre-commit==2.7.1",
    "pytest==6.1.1",
]

EXTRAS_REQUIREMENTS = {"devel": DEVEL_REQUIREMENTS}


def do_setup() -> None:
    setup(
        version=VERSION,
        packages=find_packages(include=["lss*"]),
        package_data={"lss": ["py.typed"]},
        include_package_data=True,
        extras_require=EXTRAS_REQUIREMENTS,
    )


if __name__ == "__main__":
    do_setup()
