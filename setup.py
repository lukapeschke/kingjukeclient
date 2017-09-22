from setuptools import setup, find_packages

setup(
    name="kingjukeclient",
    version="0.1dev",
    author="Luka Peschke",
    author_email="mail@lukapeschke.com",
    license="MIT",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3"
    ],
    entry_points={
        "console_scripts": ["kjuke=kingjukeclient.client:main"]
    },
    install_requires=[
        'argparse',
        'requests',
    ],
)
