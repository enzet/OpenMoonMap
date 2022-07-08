from setuptools import setup

setup(
    name="OpenMoonMap",
    version="0.1",
    packages=["openmoonmap"],
    url="https://github.com/enzet/OpenMoonMap",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    license="MIT",
    author="Sergey Vartanov",
    author_email="me@enzet.ru",
    description=(
        "Small research project on using OpenStreetMap XML format to create "
        "an open map for Moon"
    ),
    entry_points={
        "console_scripts": ["openmoonmap=openmoonmap.__main__:main"],
    },
)
