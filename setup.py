from setuptools import setup, find_packages

setup(
    name="master_data_collection",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        "requests>=2.25.0",
        "pandas>=1.2.0",
        "numpy>=1.19.0",
    ],
    author="Moon Whales",
    author_email="your.email@example.com",
    description="A comprehensive wrapper for the Hyperliquid API with advanced data collection capabilities",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/Dutchthenomad/Master-Data-Wrapper",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
)
