import argparse
import pathlib
import sys

from makros import translate_folder

# Poetry will bind the CLI to a function rather than a file and pass the
# arguments via function parameters
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

    # To ensure that test coverage is correctly supported, we need to run a 
    # specific function.
    #
    # We do not enable this by default, because I do not want to depend on
    # the coverage modules in the final build
    if args.coverage:
        print("Coverage requires the `coverage` module to be installed to function")
        import coverage
        print(
            'Coverage: Remember to set `COVERAGE_PROCESS_START` env variable')
        coverage.process_startup()

    args_path = args.file

    # If the provided path is not a file, we will assume it is a folder and use
    # the __main__.py file in it.
    if not pathlib.Path(args_path).is_file():
        args_path = pathlib.Path(args_path).joinpath("__main__.py")
        args_path = str(args_path)

    # Get the absolute path to the current file and its containing folder
    current_file = pathlib.Path(args_path).absolute()
    current_folder = pathlib.Path(current_file).parent.absolute()

    translate_folder(current_folder)

    # Stackoverflow theft! Runs the file specified in the python interpreter,
    # replacing .mpy with .py
    exec(open(current_file.replace('.mpy', '.py')).read())


if __name__ == "__main__":
    cli(sys.argv)
