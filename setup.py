"""
Setup script for Tennis Simulator package.
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read the README file
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

# Read requirements
requirements = []
with open("requirements.txt", "r") as f:
    for line in f:
        line = line.strip()
        if line and not line.startswith("#"):
            requirements.append(line)

setup(
    name="tennis-simulator",
    version="1.0.0",
    author="Tennis Simulator Team",
    author_email="team@tennissimulator.com",
    description="A comprehensive tennis tournament simulation system for ATP and WTA Grand Slam tournaments",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/tennissimulator/tennis-simulator",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Sports/Athletics",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Games/Entertainment :: Simulation",
        "Topic :: Scientific/Engineering :: Information Analysis",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=22.0.0",
            "flake8>=5.0.0",
            "mypy>=0.991",
        ],
        "docs": [
            "sphinx>=5.0.0",
            "sphinx-rtd-theme>=1.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "tennis-simulator=main:cli",
        ],
    },
    include_package_data=True,
    package_data={
        "tennis_simulator": ["data/*.txt", "data/*.json"],
    },
    keywords="tennis, simulation, tournament, atp, wta, wimbledon, scorito",
    project_urls={
        "Bug Reports": "https://github.com/tennissimulator/tennis-simulator/issues",
        "Source": "https://github.com/tennissimulator/tennis-simulator",
        "Documentation": "https://tennis-simulator.readthedocs.io/",
    },
) 