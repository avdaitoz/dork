from setuptools import setup, find_packages

setup(
    name='advaitzz',
    version='1.0',
    packages=find_packages(),
    install_requires=[
        'pandas',
        'PySimpleGUI'
    ],
    entry_points={
        'console_scripts': [
            'advaitzz=advaitzz.cli:main',
        ],
    },
)
