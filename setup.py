from setuptools import setup

setup(
    name="OpenMoonMap",
    version="0.1",
    packages=["omm"],
    url="https://github.com/enzet/OpenMoonMap",
    license="",
    author="Sergey Vartanov",
    author_email="me@enzet.ru",
    description=(
        "Small research project on using OpenStreetMap XML format to create "
        "an open map for Moon"
    ),
    entry_points={
        "console_scripts": ["omm=omm.__main__:main"],
    },
)
