from setuptools import setup, find_packages
from pathlib import Path
import os

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

def get_scenario_package_data():
    """Automatically discover all scenario files for packaging"""
    package_data = {}
    scenarios_dir = Path("clouddojo/scenarios")
    
    if scenarios_dir.exists():
        for scenario_dir in scenarios_dir.iterdir():
            if scenario_dir.is_dir() and scenario_dir.name != "__pycache__":
                # Find all non-Python files in scenario directory
                files = []
                for file_path in scenario_dir.rglob("*"):
                    if file_path.is_file() and not file_path.name.endswith(".py") and "__pycache__" not in str(file_path):
                        # Get relative path from scenario directory
                        rel_path = file_path.relative_to(scenario_dir)
                        files.append(str(rel_path))
                
                if files:
                    package_name = f"clouddojo.scenarios.{scenario_dir.name}"
                    package_data[package_name] = files
    
    return package_data

setup(
    name="clouddojo",
    version="0.1.0",
    description="A gamified, narrative-driven troubleshooting platform for DevOps/SRE engineers",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="CloudDojo Contributors",
    author_email="datakaitechnologies@gmail.com",
    url="https://github.com/datakaitech/clouddojo-cli",
    project_urls={
        "Bug Reports": "https://github.com/datakaitech/clouddojo-cli/issues",
        "Source": "https://github.com/datakaitech/clouddojo-cli",
        "Documentation": "https://github.com/datakaitech/clouddojo-cli#readme",
    },
    packages=find_packages(),
    package_data=get_scenario_package_data(),
    include_package_data=True,
    install_requires=[
        "click>=8.0.0",
        "rich>=12.0.0",
        "docker>=6.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "flake8>=5.0.0",
            "black>=22.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "clouddojo=clouddojo.cli:cli",
        ],
    },
    python_requires=">=3.8",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "Topic :: System :: Systems Administration",
        "Topic :: Education",
        "Topic :: Software Development :: Testing",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: OS Independent",
    ],
    keywords="devops sre troubleshooting learning gamification docker kubernetes",
    license="MIT",
    zip_safe=False,
)

