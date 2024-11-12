import os

from setuptools import find_packages, setup

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, "README.md")).read()


setup(
    name="shodo",
    version="1.0.1",
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
    extras_require={
        "dev": [
            "pytest",
            "pytest-mock",
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "Development Status :: 5 - Production/Stable",
        "License :: OSI Approved :: MIT License",
    ],
    entry_points={
        "console_scripts": [
            "shodo = shodo.main:cli",
        ],
    },
)
