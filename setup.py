from setuptools import setup

import iniltx

setup(
    name="iniltx",
    version=iniltx.__version__,
    description="An INI/LTX config parser",
    py_modules=["iniltx"],
    url="https://github.com/hugebrain16/iniltx",
    install_requires=[
        "iniparser @ git+https://github.com/HugeBrain16/iniparser.git@1.1.2"
    ],
)
