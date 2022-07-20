import os
import subprocess
import coverage

coverage.process_startup()

env = {
    # 'COVERAGE_PROCESS_START': os.getcwd()
}

for key in os.environ:
    env[key] = os.getenv(key)


class TestCli:
    def test_help(self):
        process = subprocess.run('makros --help --coverage',
                                 check=True,
                                 shell=True,
                                 capture_output=True,
                                 env=env)
        stdout = str(process.stdout)
        print(stdout)

        # Make sure it has the necessary information
        assert "Translates a macro python program into a python program and executes it" in stdout
        assert "The file to translate" in stdout
        assert "-h, --help  show this help message and exit" in stdout

    def test_execute(self):
        # Note: The tests run in the root directory, be sure to provide the
        # correct path
        process = subprocess.run(
            'makros tests/units/makro_example.mpy --coverage',
            check=True,
            shell=True,
            capture_output=True,
            env=env)
        stdout = str(process.stdout)
        print(stdout)

        assert "Hello, World!" in stdout