import codecs
import os
import re

import setuptools


def find_version(*file_paths):
    here = os.path.abspath(os.path.dirname(__file__))
    with codecs.open(os.path.join(here, *file_paths), "r") as fp:
        version_file = fp.read()
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]", version_file, re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError("Unable to find version string.")


setuptools.setup(
    name="mb-base1",
    version=find_version("mb_base1/__init__.py"),
    python_requires=">=3.10",
    packages=["mb_base1"],
    install_requires=[
        "fastapi==0.78.0",
        "Jinja2==3.1.2",
        "aiofiles==0.8.0",
        "itsdangerous==2.1.2",
        "WTForms==3.0.1",
        "python-multipart==0.0.5",
        "uvicorn[standard]==0.17.6",
        "gunicorn==20.1.0",
        "pyTelegramBotAPI==4.5.1",
        "mb-std~=0.4.6",
    ],
    extras_require={"dev": ["pytest==7.1.2", "pre-commit==2.19.0", "wheel==0.37.1", "twine==4.0.0", "pip-audit==2.2.1"]},
    include_package_data=True,
)
