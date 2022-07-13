import subprocess
from typing import List
from os import listdir
from os.path import join, isfile
import sys
import os

sys.path.append(os.getcwd() + '/src')
from utils import progressBar


def get_files(folder_name: str) -> List[str]:
    all_items = [join(folder_name, item) for item in listdir(folder_name)]
    files = [item for item in all_items if isfile(item)]

    return files


print("Preparing for pytest")
print("====================")

files = [file for file in get_files('./tests/macros')]

for file_name in progressBar(files):
    if not file_name.endswith('.mpy'):
        continue

    test_host = file_name.replace('.mpy',
                                  '.py').replace('./tests/macros/',
                                                 './tests/macros/test_')

    if os.path.exists(test_host):
        continue

    with open(test_host, 'w') as file:
        file.write(f'''
import pytest
from coverage.execfile import run_python_file

import sys
import os

old_cwd = os.getcwd()
sys.path.append(os.getcwd() + '/src')
from lib import translate_file
sys.path.append(old_cwd)

def test_answer():
    translate_file('{file_name}')
    run_python_file(['{file_name.replace('.mpy', '.py')}'])
''')

print("Installing global modules")
print("====================")

subprocess.run('''cd tests/macros/global
pip install -e .''',
               shell=True, check=True,
               executable='/bin/sh')

print(
    'Running pytest, if you get any errors make sure you are in a poetry shell'
)
print('\t| poetry shell')
print()

print(os.getcwd())

os.system(f'pytest --cov={os.getcwd()} --cov-report xml tests/')
