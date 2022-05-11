import argparse
import pathlib

from lib import translate_folder

cli_parser = argparse.ArgumentParser(
    description=
    "Translates a macro python program into a python program and executes it")
cli_parser.add_argument("file", type=str, help="The file to translate")
args = cli_parser.parse_args()

current_file = str(pathlib.Path(args.file).absolute())
current_folder = str(pathlib.Path(current_file).parent.absolute())

translate_folder(current_folder)

# Stackoverflow theft! Runs the file specified in the python interpreter,
# replacing .mpy with .py
exec(open(current_file.replace('.mpy', '.py')).read())