import os

from setuptools import find_packages, setup

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, "README.md")).read()


setup(
    name="shodo",
    version="0.0.9",
    packages=find_packages(),
    url="https://github.com/zenproducts/shodo-python",
    license="MIT",
    author="ZenProducts Inc.",
    description="Shodo Python CLI",
    long_description=README,
    long_description_content_type="text/markdown",
    install_requires=[
        "Click",
        "requests",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Development Status :: 3 - Alpha",
        "License :: OSI Approved :: MIT License",
    ],
    entry_points={
        "console_scripts": [
            "shodo = shodo.main:cli",
        ],
    },
)
