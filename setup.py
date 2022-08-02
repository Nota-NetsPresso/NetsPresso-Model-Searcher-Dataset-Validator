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
<<<<<<< HEAD

# python setup.py build
=======
>>>>>>> ed8490f4ac27f63e32c6b27f75094d2858f91447
