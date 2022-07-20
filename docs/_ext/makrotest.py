import doctest
from pathlib import Path
import pprint
from sphinx.ext.doctest import DoctestDirective, TestsetupDirective, TestcleanupDirective, TestcodeDirective, TestoutputDirective, DocTestBuilder

from makros.makros import Makros
from makros.parser import MakroParser


class ToParse():
    def __init__(self, text, parser: MakroParser):
        self.text = text
        self.parser = parser

    def parse(self):
        new = self.parser.parse_string(self.text).split('\n')

        print("old")
        print(self.text)
        print("new")
        print(new)

        first = new[0]
        rest = new[1:]

        return [f">>> {first}", *[f"... {other}" for other in rest]]


class Output():
    def __init__(self, text):
        self.text = text


class MacroTest(DoctestDirective):
    has_content = True

    def run(self):
        print(self.content)
        parser = Makros.get().get_parser(Path("docs/makrotest"))

        content = []

        for line in self.content:  # type: ignore
            if line.startswith('>>>'):
                content.append(ToParse(line.replace('>>>', ''), parser))
                continue

            if line.startswith('...'):
                if not isinstance(content[-1], ToParse):
                    raise Exception(
                        f"Make sure there is a '>>>' before '{line}'")

                content[-1].text += f"\n{line.replace('...', '')}"
                continue

            content.append(Output(line))

        pprint.pprint(content)

        new_content = []
        for line in content:
            if isinstance(line, ToParse):
                new_content += line.parse()
            else:
                new_content.append(line.text)

        pprint.pprint(new_content)

        self.content = new_content
        # self.name = 'doctest'

        out = DoctestDirective.run(self)

        return out


def setup(app):
    app.add_directive('testsetup', TestsetupDirective)
    app.add_directive('testcleanup', TestcleanupDirective)
    app.add_directive('macro_test', MacroTest)
    app.add_directive('testcode', TestcodeDirective)
    app.add_directive('testoutput', TestoutputDirective)
    app.add_builder(DocTestBuilder)
    # this config value adds to sys.path
    app.add_config_value('doctest_path', [], False)
    app.add_config_value('doctest_test_doctest_blocks', 'default', False)
    app.add_config_value('doctest_global_setup', '', False)
    app.add_config_value('doctest_global_cleanup', '', False)
    app.add_config_value(
        'doctest_default_flags',
        doctest.DONT_ACCEPT_TRUE_FOR_1 | doctest.ELLIPSIS | doctest.IGNORE_EXCEPTION_DETAIL,
        False)
    return {'version': '1.0.0', 'parallel_read_safe': True}
