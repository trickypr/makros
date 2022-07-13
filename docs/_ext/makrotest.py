import doctest
from sphinx.ext.doctest import DoctestDirective, TestsetupDirective, TestcleanupDirective, TestcodeDirective, TestoutputDirective, DocTestBuilder

from makros.lib import PyMacro


class ToParse():
    def __init__(self, text):
        self.text = text

    def parse(self):
        parser = PyMacro()
        new = parser.parse_string(self.text).split('\n')
        first = new[0]
        rest = new[1:]

        return [f">>> {first}", *["... {other}" for other in rest]]


class Output():
    def __init__(self, text):
        self.text = text


class MacroTest(DoctestDirective):
    has_content = True

    def run(self):
        content = []

        for line in self.content:  # type: ignore
            if content.__str__().startswith('>>>'):
                content.append(ToParse(line.replace('>>>', '')))
                continue

            if content.__str__().startswith('...'):
                if not isinstance(content[-1], ToParse):
                    raise Exception(
                        f"Make sure there is a '>>>' before '{content}'")

                content[-1].text += f"\n{line.replace('...', '')}"
                continue

            content.append(Output(line))

        new_content = []
        for line in content:
            if isinstance(line, ToParse):
                new_content += line.parse()
            else:
                new_content.append(line.text)

        self.content = new_content
        print(self.content)

        out = DoctestDirective.run(self)

        print(out)

        return out


def setup(app):
    app.add_directive('testsetup', TestsetupDirective)
    app.add_directive('testcleanup', TestcleanupDirective)
    app.add_directive('doctest', MacroTest)
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
