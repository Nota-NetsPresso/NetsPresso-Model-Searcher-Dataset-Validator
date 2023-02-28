from cx_Freeze import setup, Executable

buildOptions = dict(
    packages=["yaml", "loguru", "src"]
) 
exe = [Executable("gui.py", targetName="NetsPresso Dataset Validator", icon="nota_icon.ico", base=None)]

setup(
    name='Filter', 
    version='0.1',
    author="nota",
    description="Validator",
    options=dict(build_exe=buildOptions),
    executables=exe
)
# python setup.py build
