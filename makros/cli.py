import argparse
import pathlib
import sys

from makros import translate_folder


def cli(args=None):
    cli_parser = argparse.ArgumentParser(
        description=
        "Translates a macro python program into a python program and executes it"
    )
    cli_parser.add_argument("file", type=str, help="The file to translate")
    cli_parser.add_argument('--coverage',
                            help="Starts up coverage.py internally",
                            action="store_true")
    args = cli_parser.parse_args(args)

    if args.coverage:
        print(
            'Coverage: Remember to set `COVERAGE_PROCESS_START` env variable')
        import coverage
        coverage.process_startup()

    args_path = args.file
    if not pathlib.Path(args_path).is_file():
        args_path = pathlib.Path(args_path).joinpath("__main__.py")
        args_path = str(args_path)

    current_file = str(pathlib.Path(args_path).absolute())
    current_folder = pathlib.Path(current_file).parent.absolute()

    translate_folder(current_folder)

    # Stackoverflow theft! Runs the file specified in the python interpreter,
    # replacing .mpy with .py
    exec(open(current_file.replace('.mpy', '.py')).read())


if __name__ == "__main__":
    cli(sys.argv)
