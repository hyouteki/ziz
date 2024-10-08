from setuptools import setup, find_packages

short_description = "Minimal tool to autofill form/portal by passing urls and information"

try:
    with open("README.md", "r") as f:
        long_description = f.read()
except FileNotFoundError:
    long_description = short_description

setup(
    name="ziz",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "requests",
        "termcolor",
        "lxml",
        "transformers",
        "sentence-transformers",
    ],
    include_package_data=True,
    description=short_description,
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/hyouteki/ziz",
    author="hyouteki",
    author_email="lakshay21060@iiitd.ac.in",
    license="GPL-3.0",
)
