# Macro imported: enum
import json


class ManifestErrors(Exception):
    def __assign_enum_types__(ManifestErrors, missing_name, missing_package_name, invalid_package_name, missing_description, missing_macros):
        ManifestErrors.MissingName = missing_name
        ManifestErrors.MissingPackageName = missing_package_name
        ManifestErrors.InvalidPackageName = invalid_package_name
        ManifestErrors.MissingDescription = missing_description
        ManifestErrors.MissingMacros = missing_macros
    
    def __eq__(self, other):
        return isinstance(self, other)


class MissingName(ManifestErrors):
    def __str__(self):
        return 'MissingName'


class MissingPackageName(ManifestErrors):
    def __str__(self):
        return 'MissingPackageName'


class InvalidPackageName(ManifestErrors):
    def __str__(self):
        return 'InvalidPackageName'


class MissingDescription(ManifestErrors):
    def __str__(self):
        return 'MissingDescription'


class MissingMacros(ManifestErrors):
    def __str__(self):
        return 'MissingMacros'

ManifestErrors.__assign_enum_types__(ManifestErrors, MissingName, MissingPackageName, InvalidPackageName, MissingDescription, MissingMacros)



del(MissingName)
del(MissingPackageName)
del(InvalidPackageName)
del(MissingDescription)
del(MissingMacros)




class MacroErrors(ManifestErrors):
    def __assign_enum_types__(MacroErrors, missing_name, missing_keyword, missing_description):
        MacroErrors.MissingName = missing_name
        MacroErrors.MissingKeyword = missing_keyword
        MacroErrors.MissingDescription = missing_description
    
    def __eq__(self, other):
        return isinstance(self, other)


class MissingName(MacroErrors):
    def __str__(self):
        return 'MissingName'


class MissingKeyword(MacroErrors):
    def __str__(self):
        return 'MissingKeyword'


class MissingDescription(MacroErrors):
    def __str__(self):
        return 'MissingDescription'

MacroErrors.__assign_enum_types__(MacroErrors, MissingName, MissingKeyword, MissingDescription)



del(MissingName)
del(MissingKeyword)
del(MissingDescription)


class PackageManifest:
    bootstrap = []
    def __init__(self, manifest_path: str):
        self.path = manifest_path
        self.contents = self.read_manifest()
        self.validate_manifest()
    def validate_manifest(self) -> None:
        if 'name' not in self.contents:
            raise ManifestErrors.MissingName(f'Package manifest {self.path} is missing a name')
        if 'package' not in self.contents:
            raise ManifestErrors.MissingPackageName(f'Package manifest {self.path} is missing a package name')
        if 'package' not in self.contents:
            raise ManifestErrors.InvalidPackageName(f'Package manifest {self.path} does not have the same name as the enclosing pip package')
        if 'description' not in self.contents:
            raise ManifestErrors.MissingDescription(f'Package manifest {self.path} is missing a description')
        if 'macros' not in self.contents:
            raise ManifestErrors.MissingMacros(f'Package manifest {self.path} is missing macros')
        self.name = self.contents['name']
        self.package_name = self.contents['package']
        self.description = self.contents['description']
        self.macros = self.contents['macros']
        if 'bootstrap' in self.contents:
            self.bootstrap = self.contents['bootstrap']
        for macro_def in self.macros:
            if 'name' not in macro_def:
                raise MacroErrors.MissingName(f'Macro in package manifest {self.path} is missing a name')
            if 'keyword' not in macro_def:
                raise MacroErrors.MissingKeyword(f'Macro in package manifest {self.path} is missing a keyword')
            if 'description' not in macro_def:
                raise MacroErrors.MissingDescription(f'Macro in package manifest {self.path} is missing a description')
    def read_manifest(self) -> dict:
        with open(self.path, 'r') as manifest_file:
            return json.load(manifest_file)