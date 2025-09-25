from setuptools import setup, find_packages
from pathlib import Path

this_directory = Path(__file__).parent
long_description = ""
readme = this_directory / "README.md"
if readme.exists():
    long_description = readme.read_text(encoding="utf-8")

setup(
    name="advaitzz",
    version="1.0.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="ADVAITZZ - Google Dork generator and recon tool (CLI + GUI)",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/advaitzz/dork",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "pyfiglet",
        "PySimpleGUI",
        "pandas",
    ],
    entry_points={
        "console_scripts": [
            "advaitzz=advaitzz.advaitzz:main",
        ],
    },
    python_requires=">=3.8",
)
