"""Setup configuration for linux.py.mysql package."""
from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="linux-py-mysql",
    version="1.0.0",
    author="Linux.py.mysql Team",
    description="Enterprise-grade Python MySQL connection and operations library",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(exclude=["tests*"]),
    python_requires=">=3.7",
    install_requires=[
        "mysql-connector-python>=8.0.0,<9.0.0",
        "PyYAML>=6.0.0,<7.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0,<8.0.0",
            "pytest-cov>=4.0.0,<5.0.0",
            "pytest-mock>=3.10.0,<4.0.0",
            "coverage>=7.0.0,<8.0.0",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
)
