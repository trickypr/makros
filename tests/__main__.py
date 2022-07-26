import subprocess
from typing import List
from os import listdir
from os.path import join, isfile
import os

from rich.progress import track
from rich import print
from rich.console import Console
from rich.markdown import Markdown

def get_files(folder_name: str) -> List[str]:
    all_items = [join(folder_name, item) for item in listdir(folder_name)]
    files = [item for item in all_items if isfile(item)]

    return files


print("[bold]Preparing for pytest")
print()

files = [file for file in get_files('./tests/macros')]

for file_name in track(files, description="Generating tests"):
    if not file_name.endswith('.mpy'):
        continue

    test_host = file_name.replace('.mpy',
                                  '.py').replace('./tests/macros/',
                                                 './tests/macros/test_')

    with open(test_host, 'w') as file:
        file.write(f'''
import pytest
from coverage.execfile import run_python_file
import os
from pathlib import Path

from makros.functions import translate_file

def test_answer():
    translate_file(Path('{file_name}'))
    run_python_file(['{file_name.replace('.mpy', '.py')}'])
''')

print()
print("[bold]Installing global modules")
print()

subprocess.run('''cd tests/macros/global_template
pip install -e .''',
               shell=True,
               check=True,
               executable='/bin/sh')

print()
console = Console()
md = Markdown("""
Running pytest. If you get any errors or warnings, this might be because you are
not in a poetry shell. Try starting the poetry shell:

```
poetry shell
```
""")
console.print(md)
print()

subprocess.run(f'pytest --cov={os.getcwd()} --cov-report xml tests/',
               shell=True, check=True)
