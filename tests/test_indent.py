import io
import sys

from contextlib import redirect_stdout
from unittest import TestCase, main

from indent import Indent


def recursively_indent(string: str, levels: int, *args, **kwargs):
    if levels > 0:
        with Indent(*args, **kwargs):
            recursively_indent(string, levels - 1, *args, **kwargs)
    else:
        print(string)


Tree = dict[str, 'Tree']
def print_tree(tree: Tree):
    if not tree:
        return
    markers = [('├── ', '│   '), ('└── ', '    ')]
    children = list(tree.items())
    for key, subtree in children:
        is_last_child = (key, subtree) == children[-1]
        key_indent, subtree_indent = markers[is_last_child]
        with Indent(string=key_indent):
            print(key)
        with Indent(string=subtree_indent):
            print_tree(subtree)


class TestIndent(TestCase):
    def testPrintNoIndent(self):
        output = io.StringIO()
        with redirect_stdout(output):
            print('hello')
        self.assertEqual(output.getvalue(), 'hello\n')

    def testOneLevel(self):
        output = io.StringIO()
        with redirect_stdout(output):
            with Indent():
                print('hello')
        self.assertEqual(output.getvalue(), '    hello\n')

    def testStaticallyNested(self):
        blockstack_limit = 20
        for n in range(blockstack_limit + 1):
            code = ''
            for j in range(n):
                code += ' ' * j + 'with Indent():\n'
            code += ' ' * n + 'print("hello")'
            output = io.StringIO()
            with redirect_stdout(output):
                exec(code)
            self.assertEqual(output.getvalue(), ' ' * 4 * n + 'hello\n')

    def testRecursivelyNested(self):
        levels = -1
        with self.assertRaises(RecursionError):
            while True:
                levels += 1
                output = io.StringIO()
                with redirect_stdout(output):
                    recursively_indent('hello', levels)
                self.assertEqual(output.getvalue(), ' ' * 4 * levels + 'hello\n')
        self.assertTrue(levels > 100) # make sure recursion limit not hit instantly

    def testTrailingNewline(self):
        output = io.StringIO()
        with redirect_stdout(output):
            with Indent():
                print('hello\n')
        self.assertEqual(output.getvalue(), '    hello\n    \n')

    def testLeadingNewline(self):
        output = io.StringIO()
        with redirect_stdout(output):
            with Indent():
                print('\nhello')
        self.assertEqual(output.getvalue(), '    \n    hello\n')

    def testInterspersedNewlines(self):
        output = io.StringIO()
        with redirect_stdout(output):
            with Indent():
                print('one', 't\nwo', 'thr\nee', 'four\n', sep='')
        self.assertEqual(output.getvalue(), '''    onet
    wothr
    eefour
    \n''')

    def testSmartJoinsStream(self):
        output = io.StringIO()
        with redirect_stdout(output):
            print('hello', end='')
            with Indent():
                print('no indent')
                print('indent')
        self.assertEqual(output.getvalue(), 'hellono indent\n    indent\n')

    def testEmptyStringWrites(self):
        output = io.StringIO()
        with redirect_stdout(output):
            with Indent():
                print('', '', '', 'one', '', 't\nwo', 'thr\nee', '', '', 'four\n', '', sep='')
        self.assertEqual(output.getvalue(), '''    onet
    wothr
    eefour
    \n''')
        output = io.StringIO()
        with redirect_stdout(output):
            with Indent():
                print(end='')
                print('', end='')
        self.assertEqual(output.getvalue(), '')
        output = io.StringIO()
        with redirect_stdout(output):
            print('hello', '', sep='', end='')
            with Indent():
                print('', end='')
                print('no indent')
                print('indent')
        self.assertEqual(output.getvalue(), 'hellono indent\n    indent\n')

    def testIndentString(self):
        output = io.StringIO()
        with redirect_stdout(output):
            with Indent(string='> '):
                print()
        self.assertEqual(output.getvalue(), '> \n')

    def testNestedBlockquotes(self):
        blockstack_limit = 20
        for n in range(blockstack_limit + 1):
            code = ''
            for j in range(n):
                code += ' ' * j + 'with Indent(string="> "):\n'
            code += ' ' * n + 'print("hello")'
            output = io.StringIO()
            with redirect_stdout(output):
                exec(code)
            self.assertEqual(output.getvalue(), '> ' * n + 'hello\n')

    def testNestedMarkdown(self):
        output = io.StringIO()
        with redirect_stdout(output):
            with Indent(string='> '):
                print('Blockquoted.')
                print()
                with Indent(string='    '):
                    print('code')
                    print('more code')
                print()
                print('End of blockquote.')
        self.assertEqual(output.getvalue(), '''> Blockquoted.
> ''''''
>     code
>     more code
> ''''''
> End of blockquote.\n''')

    def testPrintsTree(self):
        tree = {'alpha':{}, 'beta': {'beta.alpha':{}, 'beta.beta':{}}, 'charlie': {'charlie.alpha':{}, 'charlie.beta':{'charlie.beta.alpha':{}}, 'charlie.charlie':{}}, 'delta':{}}
        output = io.StringIO()
        with redirect_stdout(output):
            print('.')
            print_tree(tree)
        self.assertEqual(output.getvalue(), '''.
├── alpha
├── beta
│   ├── beta.alpha
│   └── beta.beta
├── charlie
│   ├── charlie.alpha
│   ├── charlie.beta
│   │   └── charlie.beta.alpha
│   └── charlie.charlie
└── delta\n''')


if __name__ == '__main__':
    main()

