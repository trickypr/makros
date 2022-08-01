from genericpath import isdir
from os import listdir, walk
from os.path import join
import sysconfig
from pathlib import Path
import token
from tokenize import TokenInfo
from typing import Optional

from makros.registration.macro_def import MacroDef

SITE_PACKAGES = sysconfig.get_path('purelib')

PackageManifest = None


class ResolutionError(Exception):
    pass


class Resolver:
    """Is responsible for resolving errors

    Raises:
        ResolutionError: Failed to find a module, see error string for info
    """

    discovered = {}
    bootstrapped_folders = []
    cwd = Path('')

    def __init__(self):
        self.lib = None

    def add_lib(self, lib):
        """Specifies the connected PyMacro class that will be used to compile 
        macros that require bootstrapping

        Args:
            lib (PyMacro): The object that will be used to bootstrap
        """

        self.lib = lib

    def ensure_manifest_loader(self):
        """The package manifest file is bootstraped after this file is loaded,
        which may cause a race condition. As a shortcut around it, we will only
        import it when resolving external modules, well after everything has
        finished bootstrapping internally
        """

        global PackageManifest

        if PackageManifest is None:
            PackageManifest = __import__(
                'makros.registration.manifest').registration.manifest.PackageManifest

    def get_internal_path(self, resolution_string: str) -> Path:
        """Gets the path object for the macro if it is one of the ones included
        with the makros module

        Args:
            resolution_string (str): The string, roughly equivalent to the file name without its extension

        Returns:
            Path: The path object representing the macro
        """

        return Path(__file__).parent.parent.joinpath('macros').joinpath(
            f"{resolution_string}.py")

    def load_macro(self, path: Path, macro_name: str,
                   trigger_token: TokenInfo) -> MacroDef:
        """Loads a macro from a given path and returns its MacroDef

        Args:
            path (Path): The path to the python file that will represent the macro
            macro_name (str): The name of the macro
            trigger_token (TokenInfo): The token that is used to trigger the macro

        Returns:
            MacroDef: The final macro loaded from disk
        """

        return MacroDef(macro_name, trigger_token, path.__str__())

    def load_macro_from_folder(self, path: Path, macro: str,
                               registration_token: TokenInfo) -> MacroDef:
        """Loads a specific macro from its containing folder

        Args:
            path (Path): The containing folder
            macro (str): The name of the macro to be loaded
            registration_token (TokenInfo): The token that will be used to trigger the macro

        Raises:
            ResolutionError: If the manifest file doesn't specify a macro with this name

        Returns:
            MacroDef: The final loaded macro for this folder
        """

        self.ensure_manifest_loader()

        # Load the package manifest
        manifest_path = path.joinpath('macros.json')
        manifest = PackageManifest(manifest_path)

        # We want to allow the user to write mpy code to take advantage of macros
        # like enums which are very helpful for writing AST
        if path not in self.bootstrapped_folders:
            for to_bootstrap in manifest.bootstrap:
                self.lib._bootstrap_file(path.__str__(),
                                        to_bootstrap,
                                        None)

            self.bootstrapped_folders.append(path)

        # If the macro is not specified within the macro definition file, throw
        # an error
        if macro not in [macro['keyword'] for macro in manifest.macros]:
            raise ResolutionError(
                f'The macro at "{path}" does not contain the macro "{macro}"')

        # Collect the information specified in the file for this macro
        macro_index = [macro['keyword']
                       for macro in manifest.macros].index(macro)
        macro_dict = manifest.macros[macro_index]

        return MacroDef(macro, registration_token,
                        str(path.joinpath(macro_dict['file'])).replace('.mpy', '.py'))

    def find_folder_recursive(self, resolution_string: str) -> Optional[Path]:
        """Finds a folder with a specific name in the current working directory recursively

        Args:
            resolution_string (str): The string we are looking for

        Returns:
            Path: The path to this string, if any
        """

        for file in walk(str(self.cwd)):
            path = file[0]
            if isdir(path) and path.split('/')[-1] == resolution_string:
                return Path(path)

    def find_folder_pip(self, resolution_string: str) -> Optional[Path]:
        """Will attempt to find a file within the pip packages folder

        Args:
            resolution_string (str): The string that is being searched for

        Returns:
            Path: The path to the string within the pip packages folder
        """

        dirs = [
            d for d in listdir(SITE_PACKAGES)
            if isdir(join(SITE_PACKAGES, d))
        ]

        for package_directory in dirs:
            if package_directory == resolution_string:
                return Path(join(SITE_PACKAGES, package_directory))

        return None

    def resolve(self, resolution_string: str) -> MacroDef:
        """Call this function to resolve an import string, for example 'enum' or 'lib/something'

        Args:
            resolution_string (str): The string to be resolved

        Raises:
            ResolutionError: Could not resolve your specific string

        Returns:
            MacroDef: The resolved macro
        """

        # If we have already discovered something, don't waste time on logic.
        if resolution_string in self.discovered:
            return self.discovered[resolution_string]

        # If the path does not include a . then it **must** be an internal macro
        if '.' not in resolution_string:
            registration_token = TokenInfo(token.NAME, resolution_string,
                                           (0, 0), (0, 0), 0)

            # Locate where the internal macro is and return an error if it is
            # not where we expect it to be
            internal_path = self.get_internal_path(resolution_string)
            if internal_path.exists():
                return self.load_macro(internal_path, resolution_string,
                                       registration_token)

            raise ResolutionError(f"Could not resolve {resolution_string}")

        # There is a . in the name, so we can pull information like package name
        # token name and generate a registration token
        package_name = resolution_string.split('.')[0]
        token_name = resolution_string.split('.')[1]
        registration_token = TokenInfo(token.NAME, token_name, (0, 0), (0, 0),
                                       '')

        local_folder = self.find_folder_recursive(package_name)
        if local_folder is not None:
            return self.load_macro_from_folder(local_folder, token_name,
                                               registration_token)

        pip_folder = self.find_folder_pip(package_name)
        if pip_folder is not None:
            macro = self.load_macro_from_folder(pip_folder, token_name,
                                                registration_token)
            self.discovered[resolution_string] = macro
            return macro

        raise ResolutionError(f"Could not resolve {resolution_string}")
