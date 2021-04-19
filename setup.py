import setuptools
from shutil import copy
from os import getcwd

packages = setuptools.find_packages()

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="pywebofworld",
    version="0.5.0",
    author="Lachlan Marnoch",
    #    short_description=long_description,
    long_description=long_description,
    url="https://github.com/Lachimax/pywebofworlds",
    packages=setuptools.find_packages(),
    python_requires='>=3.6',
    license='Attribution-NonCommercial-ShareAlike 4.0 International'
)