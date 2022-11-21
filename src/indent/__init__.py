import re
import sys

from io import TextIOBase
from types import SimpleNamespace


class LastCharTracker:
    r'''Wraps a text stream to track the last character written to the stream'''
    def __init__(self, stream: TextIOBase):
        if stream.readable(): # try to find the last character that has already been written
            try:
                stream_position = stream.tell()
                stream.seek(stream_position - 1)
                self.last_character = stream.read(1)
                stream.seek(stream_position)
            except:
                self.last_character = None
        else:
            self.last_character = None
        for attr in filter(lambda x: not x.startswith('_'), dir(stream)):
            if attr == 'write':
                def wrapped_attr(s: str):
                    try:
                        self.last_character = s[-1]
                    except IndexError:
                        pass
                    return stream.write(s)
            elif attr == 'writelines':
                def wrapped_attr(lines: list[str]):
                    try:
                        lines = [line for line in lines if line]
                        last_line = lines[-1]
                        self.last_character = last_line[-1]
                    except IndexError:
                        pass
                    return stream.writelines(lines)
            else:
                wrapped_attr = getattr(stream, attr)
            setattr(self, attr, wrapped_attr)


class Indent:
    r'''Context manager that indents lines written to sys.stdout

    Constructor arguments:
    :param amount: the width of the indent in spaces
    :param string: the string to indent with. If set, amount should not be set.
    '''
    def __init__(self, amount: int=4, *, string: str=None):
        self.indent_string = string if string is not None else ' ' * amount

    def _write(self, s: str):
        if self._tracked_stdout.last_character in ('\n', None) and s:
            s = self.indent_string + s
        s = re.sub(r'\n(.)', r'\n' + self.indent_string + r'\1', s)
        return self._tracked_stdout.write(s)

    def _writelines(self, lines: list[str]):
        indented_lines = []
        for i, line in enumerate(lines):
            if any(lines[i + 1:]): # more characters to come
                newlines_for_indents = (r'\n', r'\n' + self.indent_string)
            else: # this is the final non-empty line, don't indent after any trailing newline
                newlines_for_indents = (r'\n(.)', r'\n' + self.indent_string + r'\1')
            indented_lines.append(re.sub(*newlines_for_indents, line))
        if self._tracked_stdout.last_character in ('\n', None):
            try:
                i, first__line = next((i, line) for i, line in enumerate(indented_lines) if line)
                indented_lines[i] = self.indent_string + first_line
            except StopIteration:
                pass
        return self._tracked_stdout.writelines(indented_lines)

    def __enter__(self):
        self._tracked_stdout = sys.stdout if isinstance(sys.stdout, LastCharTracker) else LastCharTracker(sys.stdout)
        self._original_stdout = sys.stdout
        indenting_io = SimpleNamespace()
        for attr in filter(lambda x: not x.startswith('_'), dir(self._tracked_stdout)):
            if attr == 'write':
                setattr(indenting_io, attr, self._write)
            elif attr == 'writelines':
                setattr(indenting_io, attr, self._writelines)
            else:
                setattr(indenting_io, attr, getattr(self._tracked_stdout, attr))
        sys.stdout = LastCharTracker(indenting_io)

    def __exit__(self, *args, **kwargs):
        sys.stdout = self._original_stdout


ORIGINAL_STDOUT = sys.stdout
sys.stdout = LastCharTracker(sys.stdout)

