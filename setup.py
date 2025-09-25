from setuptools import setup, find_packages

setup(
    name="advaitzz",
    version="1.0.0",
    author="shantnoo",
    author_email="promethiumxd@proton.me",
    description="ADVAITZZ - Google Dork & Recon Tool with CLI + GUI",
    long_description=open("README.md").read() if Path("README.md").exists() else "",
    long_description_content_type="text/markdown",
    url="https://github.com/advaitoz/dork",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "PySimpleGUI",
        "pyfiglet",
        "pandas"
    ],
    entry_points={
        "console_scripts": [
            "advaitzz=advaitzz.advaitzz:main",  # main function in advaitzz.py
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.7',
)
