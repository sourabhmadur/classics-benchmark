#!/usr/bin/env python3
"""
Setup script for CLASSICS-EMR package
"""

from setuptools import setup, find_packages
import os

# Read the README file
def read_readme():
    readme_path = os.path.join(os.path.dirname(__file__), 'README.md')
    if os.path.exists(readme_path):
        with open(readme_path, 'r', encoding='utf-8') as f:
            return f.read()
    return "CLASSICS-EMR: Measuring Verbatim Recall of Public-Domain Classics in Large Language Models"

# Read requirements from requirements.txt
def read_requirements():
    req_path = os.path.join(os.path.dirname(__file__), 'requirements.txt')
    if os.path.exists(req_path):
        with open(req_path, 'r') as f:
            return [line.strip() for line in f if line.strip() and not line.startswith('#')]
    return []

setup(
    name="classics-emr",
    version="0.1.0",
    description="Measuring Verbatim Recall of Public-Domain Classics in Large Language Models",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    author="CLASSICS-EMR Team",
    author_email="",
    url="https://github.com/your-username/classics_benchmark",
    
    # Package configuration
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    include_package_data=True,
    
    # Dependencies
    install_requires=read_requirements(),
    python_requires=">=3.8",
    
    # Entry points
    entry_points={
        "console_scripts": [
            "classics-emr-test=classics_emr.cli:main",
        ],
    },
    
    # Classifiers
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Researchers",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    
    # Keywords
    keywords="machine-learning nlp language-models memorization benchmark",
) 