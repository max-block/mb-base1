import codecs
import os
import re

import setuptools
from pkg_resources import parse_requirements


def find_version(*file_paths):
    here = os.path.abspath(os.path.dirname(__file__))
    with codecs.open(os.path.join(here, *file_paths), "r") as fp:
        version_file = fp.read()
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]", version_file, re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError("Unable to find version string.")


def load_requirements(f_name: str) -> list:
    requirements = []
    with open(f_name, "r") as fp:
        for req in parse_requirements(fp.read()):
            extras = "[{}]".format(",".join(req.extras)) if req.extras else ""
            requirements.append("{}{}{}".format(req.name, extras, req.specifier))  # type:ignore
    return requirements


setuptools.setup(
    name="mb-base1",
    version=find_version("mb_base1/__init__.py"),
    python_requires=">=3.9",
    packages=["mb_base1"],
    install_requires=load_requirements("requirements.txt"),
    extras_require={"dev": load_requirements("requirements-dev.txt")},
    include_package_data=True,
)
