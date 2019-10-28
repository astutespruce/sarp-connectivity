from setuptools import setup, find_packages
from os import path

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, "README.md"), encoding="utf-8") as f:
    long_description = f.read()

# Arguments marked as "Required" below must be included for upload to PyPI.
# Fields marked as "Optional" may be commented out.

setup(
    name="sarp-connectivity",
    version="2.0.1",
    description="Southeast Aquatic Barriers Inventory Visualization & Prioritization Tool",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/astutespruce/sarp-connectivity",
    author="Brendan C. Ward",
    keywords="aquatic connectivity hydrography",
    install_requires=[
        "pandas",
        "flask",
        "feather-format",
        "flask-cors",
        "gunicorn",
        "jinja2",
        "raven",
    ],
    extras_require={"dev": ["black", "pylint", "geopandas", "rtree"]},
)
