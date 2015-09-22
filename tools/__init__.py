"""
    
    ~~~
    
    By: Alex on 9/20/2015
"""
__author__ = 'Alex'
import argparse
import traceback
import sys

class ArgumentParser(argparse.ArgumentParser):
    def __init__(self, **kwargs):
        self.imp = kwargs.pop("imp")
        self.imp_message = kwargs.pop("imp_message")
        super().__init__(**kwargs)

    def error(self, message):
        if self.imp is not None and self.imp_message is not None:
            self.imp.send_message(self.imp_message.channel,
                                  "Error: {}".format(message))

def trim_docstring(docstring):
    if not docstring:
        return ""
    lines = docstring.expandtabs().splitlines()
    indent = sys.maxsize
    for line in lines[1:]:
        stripped = line.lstrip()
        if stripped:
            indent = min(indent, len(line) - len(stripped))
    trimmed = [lines[0].strip()]
    if indent < sys.maxsize:
        for line in lines[1:]:
            trimmed.append(line[indent:].rstrip())
    while trimmed and not trimmed[-1]:
        trimmed.pop()
    while trimmed and not trimmed[0]:
        trimmed.pop(0)
    return '\n'.join(trimmed)


def get_input(prompt):
    """
    Get decoded input from the terminal (equivalent to python 3's ``input``).
    """
    return input(prompt)



def get_raising_file_and_line(tb=None):
    """Return the file and line number of the statement that raised the tb.
    Returns: (filename, lineno) tuple
    """
    if not tb:
        tb = sys.exc_info()[2]

    filename, lineno, _context, _line = traceback.extract_tb(tb)[-1]

    return filename, lineno
