import json
from os import listdir
from pathlib import Path
from os.path import isfile, join
from makros.parser import MakroParser

from makros.registration.resolver import Resolver
from makros.utils import sha256sum

BOOTSTRAP_FOLDERS = ['macros', 'registration']
HASH_FILE = str(Path(__file__).parent.joinpath('macros')) + '.json'

MAKROS = None


class Makros:
    """
    Responsible for tracking the progress of expensive tasks and objects that
    should not be run more than once. These include:

    - Boostrapping the library
    - Keeping a copy of the resolver (requires bootstrapping)

    It also should be used for instantiating subclasses that depend on any of
    the above features. These include:
    
    - The parser
    """

    _resolver = Resolver()
    """Globally responsible for locating makros within the file system.
    """

    def __init__(self):
        """Constructs the Makros class, AVOID USING, USE ``.get()`` INSTEAD!
        """

        self._bootstrap()
        self._resolver.add_lib(self)

    def _bootstrap(self) -> None:
        """Will parse and convert all of the mpy files into py files so that
        other parts makros can use them, reducing the amount of code I have to
        write
        """

        # Define a fallback dictionary in case the HASH_FILE has not yet been
        # created
        macro_hash = {}

        if isfile(HASH_FILE):
            macro_hash = json.loads(open(HASH_FILE).read())

        for folder in BOOTSTRAP_FOLDERS:
            folder_path = str(Path(__file__).parent.joinpath(folder))

            # For all of the files in this folder, run bootstrap then update the
            # macro hash if it has changed to avoid future recompiles
            for file in listdir(folder_path):
                new_hash = self._bootstrap_file(folder_path, file, macro_hash)

                if new_hash:
                    macro_hash[folder_path + file] = new_hash

        # Write the hash file back to disk
        with open(HASH_FILE, 'w') as file:
            file.write(json.dumps(macro_hash))

    def _bootstrap_file(self, folder_path, file, macro_hash):
        """Will bootstrap a specific file if a similar version of that file has
        not already been boostraped

        Args:
            folder_path (str): THe folder the file will be contained in
            file (str): The file name and extension to be transpiled
            macro_hash (dict): A dictionary containing the hashes of all of the already transpiled files

        Returns:
            str: (Optional) the hash of the newly created file, if any
        """

        # If the file doesn't exist or doesn't end with .mpy, we do not want to
        # attempt to parse it
        if not isfile(join(folder_path, file)) or not file.endswith('.mpy'):
            return

        # The sha256 checksum of the file, used to determine if the file has been
        # chanced since the last time it was parsed
        file_hash = sha256sum(join(folder_path, file))

        # Will will skip if all of the following conditions are true
        #  - The macro_hash object has been defined
        #  - The macro_hash object contains this file
        #  - The file hash matches the macro_hash of this file
        is_in_hash = macro_hash is not None and folder_path + file in macro_hash
        hash_matches = is_in_hash and file_hash == macro_hash[folder_path + file]

        if hash_matches:
            return

        parser = self.get_parser(Path(join(folder_path, file)))
        parser.parse()

        # Return the new macro hash so it can be updated
        return file_hash

    def get_parser(self, path: Path) -> MakroParser:
        """Returns a parser that is instanciated with access to the global
        resolver instance.

        Args:
            path (Path): The file you plan to be parsing. You can provide a fake path if you plan on parsing a string or a token list

        Returns:
            MakroParser: The parser that you should use for parsing the file
        """

        return MakroParser(path, self)

    @staticmethod
    def get() -> "Makros":
        """Gets the global instance of Makros. Makros should be a singleton for
        performance, hence the get method

        Returns:
            Makros: An instance of the makros object
        """

        global MAKROS

        if MAKROS is None:
            MAKROS = Makros()

        return MAKROS
