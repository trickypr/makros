import pathlib
from lib import PyMacro

test_file = pathlib.Path(__file__).parent.parent.joinpath('tests/macroImp.mpy')

macro = PyMacro()
macro.parse_file(test_file)