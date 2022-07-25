from makros.makros import Makros
from pathlib import Path


def translate_file(path: Path):
    """Parses a file and writes its output to disk at the same location with ".mpy" replaced with ".py"

    Args:
        path: The path to the file you want to parse
    """

    parser = Makros.get().get_parser(path)
    parser.parse()


def translate_folder(folder_path: Path):
    """Will parse all ".mpy" files within a folder and write their contents to disk

    Args:
        folder_path (Path): The path to the folder you want to parse
    """

    for file in folder_path.iterdir():
        if file.is_dir():
            translate_folder(file)
            continue

        if file.suffix == '.mpy':
            translate_file(file)
