from cx_Freeze import setup, Executable 
import sys 

buildOptions = dict(
    packages=["yaml","loguru", "src"],
) 
exe = [Executable("gui.py")]

setup(
    name='Filter', 
    version='0.1',
    author="nota",
    description="Validator",
    options=dict(build_exe=buildOptions),
    executables=exe
)
# python setup.py build
