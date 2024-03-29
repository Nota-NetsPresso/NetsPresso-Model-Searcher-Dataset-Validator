from cx_Freeze import setup, Executable

buildOptions = dict(
    packages=["yaml", "loguru", "src"]
) 
exe = [Executable("gui.py", targetName="NetsPresso Dataset Validator.exe", icon="nota_icon.ico")]

setup(
    name='Filter', 
    version='0.1',
    author="nota",
    description="Validator",
    options=dict(build_exe=buildOptions),
    executables=exe
)
# python setup.py build
