import json
from os import listdir
from pathlib import Path
from os.path import isfile, join
from makros.parser import MakroParser


from makros.registration.resolver import Resolver
from makros.utils import progressBar, sha256sum


BOOTSTRAP_FOLDERS = ['macros', 'registration']
HASH_FILE = Path(__file__).parent.joinpath('macros').__str__() + '.json'

makros = None


class Makros:
    resolver = Resolver()

    def __init__(self):
        self.bootstrap()
        self.resolver.add_lib(self)

    def bootstrap(self) -> None:
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
            folder_path = Path(__file__).parent.joinpath(folder).__str__()

            # For all of the files in this folder, run bootstrap then update the
            # macro hash if it has changed to avoid future recompiles
            for file in progressBar(listdir(folder_path), 'Parsing macros'):
                new_hash = self.bootstrap_file(folder_path, file, macro_hash)

                if new_hash:
                    macro_hash[folder_path + file] = new_hash

        # Write the hash file back to disk
        with open(HASH_FILE, 'w') as file:
            file.write(json.dumps(macro_hash))

    def bootstrap_file(self, folder_path, file, macro_hash):
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
        if macro_hash is not None and macro_hash.__contains__(
                folder_path + file) and file_hash == macro_hash[folder_path +
                                                                file]:
            return

        MakroParser(Path(join(folder_path, file)), self).parse()

        # Return the new macro hash so it can be updated
        return file_hash

    def get_parser(self, path: Path) -> MakroParser:
        return MakroParser(path, self)

    def get() -> "Makros":
        global makros

        if makros is None:
            makros = Makros()

        return makros
