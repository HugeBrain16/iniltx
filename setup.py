from setuptools import setup

setup(
    name="iniltx",
    version="1.0.0-dev5",
    description="An INI/LTX config parser",
    py_modules=["iniltx"],
    url="https://github.com/hugebrain16/iniltx",
    install_requires=["iniparser @ git+https://github.com/HugeBrain16/iniparser@1.2.0"],
)
