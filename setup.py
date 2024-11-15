import os

from setuptools import find_packages, setup

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, "README.md")).read()


setup(
    name="shodo",
    version="1.1.0",
    packages=find_packages(exclude=["tests"]),
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
        "async": [
            "aiohttp",
        ],
        "dev": [
            "aioresponses",
            "pytest",
            "pytest-asyncio",
            "pytest-mock",
            "pytest-responses",
            "mypy",
            "types-requests",
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
    package_data={
        "shodo": [
            "py.typed",
        ],
    },
    python_requires=">=3.8",
)
