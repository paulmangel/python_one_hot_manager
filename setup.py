from setuptools import setup, find_packages

setup(
    name='one-hot-module',
    version='1.0.0',
    description='A module for managing one-hot encoding in Python.',
    author='Paul Mangel',
    packages=find_packages(),
    install_requires=[
        'pandas',
        'numpy'
    ],
)