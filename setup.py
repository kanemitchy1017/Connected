"""
Connected - Bluetooth Device Battery Monitor
Setup script for creating executable
"""

from setuptools import setup, find_packages
import os

# Get the long description from the README file
here = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

# Get requirements
with open(os.path.join(here, 'requirements.txt'), encoding='utf-8') as f:
    requirements = [line.strip() for line in f if line.strip() and not line.startswith('#')]

setup(
    name="connected",
    version="0.2.0",
    author="Connected Project",
    author_email="",
    description="Windows 11用Bluetoothデバイス バッテリー監視アプリケーション",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/your-username/connected",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Operating System :: Microsoft :: Windows :: Windows 10",
        "Operating System :: Microsoft :: Windows :: Windows 11",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: System :: Hardware",
        "Topic :: Utilities",
    ],
    python_requires=">=3.9",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-asyncio>=0.18.0",
            "black>=22.0",
            "pylint>=2.12",
            "mypy>=0.910",
        ]
    },
    entry_points={
        "console_scripts": [
            "connected=main:main",
        ],
    },
    include_package_data=True,
    package_data={
        "": ["resources/icons/*", "resources/translations/*"],
    },
)
