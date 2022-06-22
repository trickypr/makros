from genericpath import isdir
from os import listdir, path
import sysconfig
from pathlib import Path
import token
from tokenize import TokenInfo
from registration.macro_def import MacroDef

SITE_PACKAGES = sysconfig.get_path('purelib')

PackageManifest = None


class ResolutionError(Exception):
    pass


class Resolver:
    discovered = {}
    bootstrapped_folders = []
    cwd = Path('')

    def __init__(self):
        self.lib = None

    def add_lib(self, lib):
        self.lib = lib

    def ensure_manifest_file(self):
        """The package manifest file is bootstraped after this file is loaded, 
        which may cause a race condition. As a shortcut around it, we will only
        import it when resolving external modules, well after everything has
        finished bootstrapping internally
        """

        global PackageManifest

        if PackageManifest is None:
            PackageManifest = __import__(
                'registration.manifest').manifest.PackageManifest

    def get_internal_path(self, resolution_string: str) -> Path:
        py = Path(__file__).parent.parent.joinpath('macros').joinpath(
            f"{resolution_string}.py")

        return py

    def load_macro(self, path: Path, macro_name: str,
                   trigger_token: TokenInfo) -> MacroDef:
        macro = MacroDef(macro_name, trigger_token, path.__str__())
        return macro

    def load_macro_from_folder(self, path: Path, macro: str,
                               registration_token: TokenInfo) -> MacroDef:
        self.ensure_manifest_file()

        manifest_path = path.joinpath('macros.json')
        manifest = PackageManifest(manifest_path)

        # We want to allow the user to write mpy code to take advantage of macros
        # like enums which are very helpful for writing AST
        if path not in self.bootstrapped_folders:
            for to_bootstrap in manifest.bootstrap:
                self.lib.bootstrap_file(path.__str__(),
                                        path.joinpath(to_bootstrap).__str__(),
                                        None)

            self.bootstrapped_folders.append(path)

        if macro not in [macro['keyword'] for macro in manifest.macros]:
            raise ResolutionError(
                f'The macro at "{path}" does not contain the macro "{macro}"')

        macro_index = [macro['keyword']
                       for macro in manifest.macros].index(macro)
        macro_dict = manifest.macros[macro_index]

        return MacroDef(macro, registration_token,
                        path.joinpath(macro_dict['file']).__str__())

    def find_folder_recursive(self, resolution_string: str) -> Path:
        for path in self.cwd.rglob('*'):
            if path.is_dir() and path.name == resolution_string:
                return path

    def find_folder_pip(self, resolution_string: str) -> Path:
        dirs = [
            d for d in listdir(SITE_PACKAGES)
            if isdir(path.join(SITE_PACKAGES, d))
        ]

        for dir in dirs:
            if dir == resolution_string:
                return Path(dir)

    def resolve(self, resolution_string: str) -> MacroDef:
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
                                       0)

        local_folder = self.find_folder_recursive(package_name)
        if local_folder is not None:
            return self.load_macro_from_folder(local_folder, token_name,
                                               registration_token)

        pip_folder = self.find_folder_pip(package_name)
        if pip_folder is not None:
            macro = self.load_macro_from_folder(local_folder)
            self.discovered[resolution_string] = macro
            return macro

        raise ResolutionError(f"Could not resolve {resolution_string}")
