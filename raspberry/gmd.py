import shlex
import sys
import re

from io import StringIO


class Gmd_tag(object):
    """Gmd tag"""

    def __init__(self, args):
        super(Gmd_tag, self).__init__()
        self.args = args
        self.children = []

    # print(args)

    def getlist(self, *keys,default=None):
        if any(isinstance(el, int) for el in keys):
            return [self.args[key] for key in keys]
        elif any(isinstance(el, str) for el in keys):
            return [self.find_child(key) or default for key in keys]
        else:
            raise TypeError('Expected int or string')

    def get(self, key, *, default=None, arg=None):
        if isinstance(key, int):
            return self.args[key] if key < len(self.args) else default
        elif isinstance(key, str):
            if arg:
                t = self.find_child(key)
                return t.args[arg] if t and arg < len(t.args) else default
            else:
                return self.find_child(key) or default

        else:
            raise TypeError('Expected int or string')

    def getchildren(self):
        return self.children

    def __iter__(self):
        return iter(self.children)

    def find_child(self, name):
        for c in self.children:
            if name == c.args[0]:
                return c
        return None

    def __getitem__(self, key):
        #print(type(key))
        if isinstance(key, int):                                # gmd[i] -> arg[i]
            return self.args[key]
        elif isinstance(key, str):                              # gmd[str] -> child where child[1] == str
            return self.find_child(key)
        else:
            raise KeyError('Expected int, string or list')

    def readchildren(self, _input):
        temp = _input.readline()
        while temp:
            temp = temp.split('#')[0].strip()
            if temp == 'end':
                return
            elif temp.startswith('#') or not temp:
                pass
            elif temp.endswith(':'):
                # print('!')
                t = Gmd_tag(shlex.split(temp[:-1]))
                t.readchildren(_input)
                self.children.append(t)
            # print('!2')
            else:
                t = Gmd_tag(shlex.split(temp))
                self.children.append(t)
            temp = _input.readline()

    def _print(self, tab=0):
        print('  ' * tab + str(self.args))
        # print(self)
        for c in self.children:
            # print(c)
            c._print(tab + 1)

    regexp = re.compile(r'\s')

    def writechildren(self, _output, tab=0):
        _output.write('\t' * tab)
        for arg in self.args:
            if self.regexp.search(arg) is not None:
                _output.write('"' + arg + '" ')
            else:
                _output.write(arg + ' ')

        if len(self.children) == 0:
            _output.write('\n')
        else:
            _output.write(':\n')
            for c in self.children:
                c.writechildren(_output, tab + 1)
            _output.write('\t' * tab + 'end\n')

    def dump(self, _output, full=False):
        if(full):
            self.writechildren(_output)
        else:
            for c in self.children:
                c.writechildren(_output, 0)

    def __str__(self):
        with StringIO() as output:
            self.dump(output, True)
            return output.getvalue()



class Gmd(Gmd_tag):
    """Gmd parser v0.1"""

    def __init__(self):
        super(Gmd, self).__init__([''])

    def parse(self, _input):
        self.args = [_input.name]
        line = _input.readline()
        while line:
            line = line.split('#')[0].strip()
            if line.startswith('#') or not line:
                pass
            elif line == 'end':
                print('Found an extra "end", lost anything?')
            elif line.endswith(':'):
                # print('!')
                t = Gmd_tag(shlex.split(line[:-1]))
                t.readchildren(_input)
                self.children.append(t)
            # print('!2')
            else:
                t = Gmd_tag(shlex.split(line))
                self.children.append(t)
            line = _input.readline()




if __name__ == "__main__":
    g = Gmd()
    with open(sys.argv[1], 'r+') as _input:
        g.parse(_input)
        g._print()

        # print(len(g.children))
