#!/usr/bin/env python3
"""
Setup script for Hyperliquid Data Collection Suite.
"""

from setuptools import setup, find_packages

setup(
    name="hyperliquid-data-suite",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        'requests>=2.28.1',
    ],
    author="Your Name",
    author_email="your.email@example.com",
    description="A comprehensive Python package for collecting data from Hyperliquid API.",
    long_description=open('README.md').read(),
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/hyperliquid-data-suite",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.8',
)
