# -*- coding: utf-8 -*-

'''
mint - small, fast and simple template engine.
'''

import os
import re
import ast
import mmap
import time
import fnmatch
import logging
import weakref
import itertools
import htmlentitydefs
from ast import Load, Store, Param
from StringIO import StringIO
from functools import partial
from collections import deque
from xml.etree.ElementTree import TreeBuilder as _TreeBuilder, Element

from lexify import *
from parse import *
from visit import AstWrapper, MintToPythonTransformer, SlotsGetter
from utils import Utils

def base_tokenizer(fp):
    'Tokenizer. Generates tokens stream from te'
    if isinstance(fp, StringIO):
        template_file = fp
        size = template_file.len
    else:
        #empty file check
        if os.fstat(fp.fileno()).st_size == 0:
            yield TOKEN_EOF, 'EOF', 0, 0
            return
        template_file = mmap.mmap(fp.fileno(), 0, access=mmap.ACCESS_READ)
        size = template_file.size()
    lineno = 0
    while 1:
        lineno += 1
        pos = 1

        # end of file
        if template_file.tell() == size:
            yield TOKEN_EOF, 'EOF', lineno, 0
            break

        # now we tokinize line by line
        line = template_file.readline().decode('utf-8')
        line = line.replace('\r\n', '')
        line = line.replace('\n', '')
        # ignoring non XML comments
        if re_comment.match(line):
            continue

        last_text = deque()
        while line:
            line_len = len(line)
            for token in tokens:
                m = token.regex.match(line)
                if m:
                    if last_text:
                        yield TOKEN_TEXT, ''.join(last_text), lineno, pos
                        pos += len(last_text)
                        last_text.clear()
                    offset, value = m.end(), m.group()
                    line = line[offset:]
                    yield token, value, lineno, pos
                    pos += offset
                    break

            # we did not get right in tokens list, so next char is text
            if line_len == len(line):
                last_text.append(line[0])
                line = line[1:]

        if last_text:
            yield TOKEN_TEXT, ''.join(last_text), lineno, pos
            pos += len(last_text)
            last_text.clear()
        yield TOKEN_NEWLINE, '\n', lineno, pos

    # all work is done
    template_file.close()


def indent_tokenizer(tokens_stream):
    current_indent = 0
    indent = 0
    for tok in tokens_stream:
        token, value, lineno, pos = tok
        # backslashed line transfer
        if token is TOKEN_BACKSLASH:
            next_tok = tokens_stream.next()
            next_token, next_value, next_lineno, next_pos = next_tok
            if next_token is TOKEN_NEWLINE:
                next_tok = tokens_stream.next()
                while next_tok[0] in (TOKEN_WHITESPACE, TOKEN_NEWLINE):
                    next_tok = tokens_stream.next()
                # first not newline or whitespace token
                yield next_tok
                continue
            yield tok
            tok = next_tok
            token, value, lineno, pos = next_tok
        # indenting and unindenting
        if token is TOKEN_NEWLINE or (token is TOKEN_WHITESPACE and (lineno, pos) == (1, 1)):
            if token is TOKEN_NEWLINE:
                yield tok
                next_tok = tokens_stream.next()
                while next_tok[0] is TOKEN_NEWLINE:
                    next_tok = tokens_stream.next()
            else:
                next_tok = tok
            next_token, next_value, next_lineno, next_pos = next_tok
            if next_token is TOKEN_WHITESPACE:
                ws_count = len(next_value)
                if indent == 0:
                    indent = ws_count
                if ws_count >= indent:
                    times = ws_count/indent
                    rest = ws_count % indent
                    range_ = times - current_indent
                    if range_ > 0:
                        # indenting
                        tmp_curr_indent = current_indent
                        for i in range(range_):
                            yield TOKEN_INDENT, ' '*indent, next_lineno, (i+tmp_curr_indent)*indent+1
                            current_indent += 1
                    elif range_ < 0:
                        # unindenting
                        for i in range(abs(range_)):
                            yield TOKEN_UNINDENT, ' '*indent, next_lineno, next_pos
                            current_indent -= 1
                    if rest:
                        yield TOKEN_WHITESPACE, ' '*rest, next_lineno, times*indent+1
                    continue
            # next token is the whitespace lighter than indent or any other
            # token, so unindenting to zero level
            for i in range(current_indent):
                yield TOKEN_UNINDENT, ' '*indent, lineno, pos
            current_indent = 0
            yield next_tok
            # we do not yielding newline tokens
            continue
        yield tok


def tokenizer(fileobj):
    return indent_tokenizer(base_tokenizer(fileobj))

############# LEXER END



def unescape(obj):
    text = unicode(obj)
    for k, v in UNSAFE_CHARS_ENTITIES_REVERSED:
        text = text.replace(k, v)
    return text


class TemplateError(Exception): pass

# variables names (we do not want to override user variables and vise versa)
from visit import TREE_FACTORY, MAIN_FUNCTION, ESCAPE_HELLPER







def _correct_inheritance(new_slots, old_slots):
    slots = {}
    for k, value in new_slots.items():
        if k in old_slots:
            name = '__base__'
            old_value = old_slots[k]
            ast_ = AstWrapper(old_value.lineno + 1, old_value.col_offset)
            value.body.insert(0, ast_.Assign(targets=[ast_.Name(id=name, ctx=Store())],
                                             value=ast_.Name(id=old_value.name)))
            del old_slots[k]
            # this slot is overrided in child template
            old_slots[k+'__overrided'] = old_value
        slots[k] = value
    slots.update(old_slots)
    return slots


def get_mint_tree(tokens_stream):
    '''
    This function is wrapper to normal parsers (tag_parser, block_parser, etc.).
    Returns mint tree.
    '''
    smart_stack = RecursiveStack()
    block_parser.parse(tokens_stream, smart_stack)
    return MintTemplate(body=smart_stack.stack)


############# API
class TemplateNotFound(Exception):
    pass


class TreeBuilder(_TreeBuilder):
    'Tree with root element already set'
    def __init__(self, *args, **kwargs):
        _TreeBuilder.__init__(self, *args, **kwargs)
        self.start('root', {})

    def to_unicode(self):
        class dummy: pass
        data = []
        out = dummy()
        out.write = data.append
        # out - fast writable object
        self.end('root')
        root = self.close()
        if root.text:
            out.write(root.text)
        for node in root:
            self._node_to_unicode(out, node)
        if root.tail:
            out.write(root.tail)
        return Markup(u''.join(data))

    def _node_to_unicode(self, out, node):
        #NOTE: all data must be escaped during tree building
        tag = node.tag
        items = node.items()
        selfclosed = ['link', 'input', 'br', 'hr', 'img', 'meta']
        out.write(u'<' + tag)
        if items:
            items.sort() # lexical order
            for k, v in items:
                out.write(u' %s="%s"' % (k, v))
        if tag in selfclosed:
            out.write(u' />')
        else:
            out.write(u'>')
            if node.text or len(node):
                if node.text:
                    out.write(node.text)
                for n in node:
                    self._node_to_unicode(out, n)
            out.write(u'</' + tag + '>')
            if node.tail:
                out.write(node.tail)


class PprintTreeBuilder(_TreeBuilder):
    'Tree with root element already set'
    def __init__(self, *args, **kwargs):
        _TreeBuilder.__init__(self, *args, **kwargs)
        self.start('root', {})
        self._level = -1

    @property
    def indention(self):
        return self._level > 0 and '  '*self._level or ''

    def to_unicode(self):
        class dummy: pass
        data = []
        out = dummy()
        out.write = data.append
        # out - fast writable object
        self.end('root')
        root = self.close()
        if root.text:
            out.write(self.indent_text(root.text))
            out.write('\n')
        for node in root:
            self._node_to_unicode(out, node)
        if root.tail:
            out.write(self.indent_text(root.tail))
        return Markup(u''.join(data))

    def _node_to_unicode(self, out, node):
        #NOTE: all data must be escaped during tree building
        self.indent()
        tag = node.tag
        items = node.items()
        selfclosed = ['link', 'input', 'br', 'hr', 'img', 'meta']
        children = list(node)
        text = node.text
        tail = node.tail
        out.write(self.indention)
        out.write(u'<' + tag)
        if items:
            items.sort() # lexical order
            for k, v in items:
                out.write(u' %s="%s"' % (k, v))
        if tag in selfclosed:
            out.write(u' />')
        else:
            out.write(u'>')
            if text:
                if text.endswith('\n'):
                    text = text[:-1]
                self.indent()
                out.write('\n')
                out.write(self.indent_text(text))
                out.write('\n')
                self.unindent()
            if children:
                out.write('\n')
                for n in children:
                    self._node_to_unicode(out, n)

            if children or text:
                out.write(self.indention)
            out.write(u'</' + tag + '>')
            if node.tail:
                out.write('\n')
                tail = node.tail
                if tail.endswith('\n'):
                    tail = tail[:-1]
                out.write(self.indent_text(tail))
        out.write('\n')
        self.unindent()

    def indent_text(self, text):
        return '\n'.join([self.indention+t for t in text.split('\n')])

    def indent(self):
        self._level += 1
    def unindent(self):
        self._level -= 1


def new_tree(pprint):
    def wrapper():
        tree = pprint and PprintTreeBuilder() or TreeBuilder()
        return tree, tree.start, tree.end, tree.data
    return wrapper


class Template(object):

    def __init__(self, source, filename=None, loader=None, globals=None, pprint=False):
        assert source or filename, 'Please provide source code or filename'
        self.source = source
        self.filename = filename if filename else '<string>'
        self._loader = loader
        self.compiled_code = compile(self.tree(), self.filename, 'exec')
        self.globals = globals or {}
        self.pprint = pprint

    def tree(self, slots=None):
        slots = slots or {}
        source = StringIO(self.source) if self.source else open(self.filename, 'r')
        mint_tree = get_mint_tree(tokenizer(source))
        tree = MintToPythonTransformer().visit(mint_tree)
        slots_getter = SlotsGetter()
        slots_getter.visit(tree.body[0])
        _slots, base_template_name = slots_getter.slots, slots_getter.base
        # we do not want to override slot's names,
        # so prefixing existing slots with underscore
        slots = _correct_inheritance(slots, _slots)
        if base_template_name:
            base_template = self._loader.get_template(base_template_name)
            tree = base_template.tree(slots=slots)
        elif slots is not None:
            # insert implementation of slots
            # def slot_bb13e100d5(): ...
            # and insert assings of slots
            # real_slot_name = slot_bb13e100d5
            for k,v in slots.items():
                if not k.endswith('__overrided'):
                    ast_ = AstWrapper(v.lineno, v.col_offset)
                    tree.body.insert(0, ast_.Assign(targets=[ast_.Name(id=k, ctx=Store())],
                                                     value=ast_.Name(id=v.name)))
                tree.body.insert(0, v)
        # tree already has slots definitions and ready to be compiled
        return tree

    def render(self, **kwargs):
        ns = {
            'utils':Utils,
            ESCAPE_HELLPER:escape,
            TREE_FACTORY:new_tree(self.pprint),
        }
        ns.update(self.globals)
        ns.update(kwargs)
        exec self.compiled_code in ns
        # execute template main function
        return ns[MAIN_FUNCTION]()

    def slot(self, name, **kwargs):
        ns = {
            'utils':Utils,
            ESCAPE_HELLPER:escape,
            TREE_FACTORY:new_tree(self.pprint),
        }
        ns.update(self.globals)
        ns.update(kwargs)
        exec self.compiled_code in ns
        return ns[name]


class Loader(object):

    def __init__(self, *dirs, **kwargs):
        self.dirs = []
        # dirs - list of directories. Order matters
        for d in dirs:
            self.dirs.append(os.path.abspath(d))
        self.cache = kwargs.get('cache', False)
        self._templates_cache = {}
        self.globals = kwargs.get('globals', {})
        self.pprint = kwargs.get('pprint', 0)

    def get_template(self, template):
        if template in self._templates_cache:
            return self._templates_cache[template]
        for dir in self.dirs:
            location = os.path.join(dir, template)
            if os.path.exists(location) and os.path.isfile(location):
                with open(location, 'r') as f:
                    tmpl = Template(source=f.read(), filename=f.name,
                                    loader=self, globals=self.globals, pprint=self.pprint)
                    if self.cache:
                        self._templates_cache[template] = tmpl
                    return tmpl
        raise TemplateNotFound(template)

    def __add__(self, other):
        dirs = self.dirs + other.dirs
        return self.__class__(cache=self.cache, globals=self.globals,*dirs)


class Looper:
    'Cool class taken from PPA project'
    class _Item:
        def __init__(self, index, has_next):
            self.index = index
            self.has_next = has_next
            self.last = not has_next
            self.first = not index
        @property
        def odd(self):
            return self.index % 2
        @property
        def even(self):
            return not self.index % 2
        def cycle(self, *args):
            'Magic method (adopted ;)'
            return args[self.index % len(args)]

    def __init__(self, iterable):
        self._iterator = iter(iterable)

    def _shift(self):
        try:
            self._next = self._iterator.next()
        except StopIteration:
            self._has_next = False
        else:
            self._has_next = True

    def __iter__(self):
        self._shift()
        index = 0
        while self._has_next:
            value = self._next
            self._shift()
            yield value, self._Item(index, self._has_next)
            index += 1


############# API END

class Printer(ast.NodeVisitor):
    'AST printer'

    def __init__(self):
        self._indent = 0
        self._indent_tab = '    '
        self.src = StringIO()
        self.write = self.src.write
        self._in_args = False
        self._in_if = False

    def make_tab(self):
        self.src.write(self._indent*self._indent_tab)

    def visit_FunctionDef(self, node):
        self.make_tab()
        self.src.write('def %s(' % node.name)
        self._in_args = True
        total_args = len(node.args.args)
        default_args_len = len(node.args.defaults) if node.args.defaults else 0
        for i, arg in enumerate(node.args.args):
            if i != 0:
                self.src.write(', ')
            self.visit(arg)
            if default_args_len > 0 and i >= (total_args - default_args_len):
                self.src.write('=')
                y = (total_args - default_args_len) - i
                self.visit(node.args.defaults[y])
        self._in_args = False
        self.src.write('):\n')
        self._indent += 1
        for n in node.body:
            self.visit(n)
        self._indent -= 1

    def visit_Return(self, node):
        self.make_tab()
        self.src.write('return ')
        self.visit(node.value)

    def visit_Name(self, node):
        self.src.write(node.id)

    def visit_Str(self, node):
        self.src.write('%r' % node.s)

    def visit_Num(self, node):
        self.src.write('%d' % node.n)

    def visit_Pass(self, node):
        self.make_tab()
        self.src.write('pass\n')

    def visit_If(self, node):
        self.make_tab()
        if self._in_if:
            self.src.write('elif ')
        else:
            self.src.write('if ')
        self.visit(node.test)
        self.src.write(':\n')
        self._indent += 1
        for n in node.body:
            self.visit(n)
        self._indent -= 1
        if node.orelse:
            self._in_if = True
            if not isinstance(node.orelse[0], ast.If):
                self.make_tab()
                self.src.write('else:\n')
                self._indent += 1
            for orelse in node.orelse:
                self.visit(orelse)
            if not isinstance(node.orelse[0], ast.If):
                self._indent -= 1
            self._in_if = False

    def visit_Compare(self, node):
        self.visit(node.left)
        self.src.write(' ')
        for op in node.ops:
            self.visit(op)
        self.src.write(' ')
        for comp in node.comparators:
            self.visit(comp)

    def visit_For(self, node):
        self.make_tab()
        self.write('for ')
        self.visit(node.target)
        self.write(' in ')
        self._in_args = True
        self.visit(node.iter)
        self._in_args = False
        self.write(':\n')
        self._indent += 1
        for n in node.body:
            self.visit(n)
        self._indent -= 1

    def visit_Tuple(self, node):
        self.src.write('(')
        for i,el in enumerate(node.elts):
            if i != 0:
                self.src.write(', ')
            self.visit(el)
        self.src.write(')')

    def visit_List(self, node):
        self.src.write('[')
        for i,el in enumerate(node.elts):
            if i != 0:
                self.src.write(', ')
            self.visit(el)
        self.src.write(']')

    def visit_Dict(self, node):
        self.src.write('{')
        total_keys = len(node.keys)
        for i in range(total_keys):
            if i != 0:
                self.src.write(', ')
            self.visit(node.keys[i])
            self.src.write(': ')
            self.visit(node.values[i])
        self.src.write('}')

    def visit_Assign(self, node):
        self.make_tab()
        for i, target in enumerate(node.targets):
            if i != 0:
                self.src.write(', ')
            self.visit(target)
        self.src.write(' = ')
        self._in_args = True
        self.visit(node.value)
        self._in_args = False
        self.src.write('\n')

    def visit_Call(self, node):
        if self._in_args:
            self.visit(node.func)
            self.src.write('(')
            for i, arg in enumerate(node.args):
                if i != 0:
                    self.src.write(', ')
                self.visit(arg)
            self.src.write(')')
        else:
            self.make_tab()
            self.visit(node.func)
            self.src.write('(')
            self._in_args = True
            for i, arg in enumerate(node.args):
                if i != 0:
                    self.src.write(', ')
                self.visit(arg)
            self.src.write(')')
            self._in_args = False
            self.src.write('\n')

    def visit_Attribute(self, node):
        self.visit(node.value)
        self.src.write('.')
        self.src.write(node.attr)

    def visit_BinOp(self, node):
        self.visit(node.left)
        self.src.write(' ')
        self.visit(node.op)
        self.src.write(' ')
        self.visit(node.right)

    def visit_BoolOp(self, node):
        for i, n in enumerate(node.values):
            self.visit(n)
            if not i:
                self.src.write(' ')
                self.visit(node.op)
                self.src.write(' ')

    # Operators
    def visit_Add(self, node):
        self.src.write('+')
    def visit_Mod(self, node):
        self.src.write('%')
    def visit_Eq(self, node):
        self.src.write('==')
    def visit_NotEq(self, node):
        self.src.write('!=')
    def visit_Lt(self, node):
        self.src.write('<=')
    def visit_Gt(self, node):
        self.src.write('>=')
    def visit_Or(self, node):
        self.src.write('or')


def all_files_by_mask(mask):
    for root, dirs, files in os.walk('.'):
        for basename in files:
            if fnmatch.fnmatch(basename, mask):
                filename = os.path.join(root, basename)
                yield filename


def render_templates(*templates, **kw):
    loader = kw['loader']
    for template_name in templates:
        result = loader.get_template(template_name).render()
        if result:
            open(template_name[:-4]+'html', 'w').write(result)


def iter_changed(interval=1):
    mtimes = {}
    while 1:
        for filename in all_files_by_mask('*.mint'):
            try:
                mtime = os.stat(filename).st_mtime
            except OSError:
                continue
            old_time = mtimes.get(filename)
            if old_time is None:
                mtimes[filename] = mtime
                continue
            elif mtime > old_time:
                mtimes[filename] = mtime
                yield filename
        time.sleep(interval)


if __name__ == '__main__':
    import datetime
    from optparse import OptionParser
    parser = OptionParser()
    parser.add_option('-c', '--code', dest='code', action='store_true',
                      default=False,
                      help='Show only python code of compiled template.')
    parser.add_option('-t', '--tokenize', dest='tokenize', action='store_true',
                      default=False,
                      help='Show tokens stream of template.')
    parser.add_option('-r', '--repeat', dest='repeat',
                      default=0, metavar='N', type='int',
                      help='Try to render template N times and display average time result.')
    parser.add_option('-p', '--pprint', dest='pprint', action='store_true',
                      default=False,
                      help='Turn pretty print on.')
    parser.add_option('-m', '--monitor', dest='monitor', action='store_true',
                      default=False,
                      help='Monitor current directory and subdirectories for changes in mint files. '
                           'And render corresponding html files.')
    (options, args) = parser.parse_args()
    loader = Loader('.', pprint=options.pprint)
    if len(args) > 0:
        template_name = args[0]
        template = loader.get_template(template_name)
        if options.code:
            printer = Printer()
            printer.visit(template.tree())
            print printer.src.getvalue()
        elif options.tokenize:
            for t in tokenizer(StringIO(template.source)):
                print t
        else:
            print template.render()
        if options.repeat > 0:
            now = datetime.datetime.now
            results = []
            for i in range(options.repeat):
                start = now()
                template.render()
                results.append(now() - start)
            print 'Total time (%d repeats): ' % options.repeat, reduce(lambda a,b: a+b, results)
            print 'Average:                 ', reduce(lambda a,b: a+b, results)/len(results)
    elif options.monitor:
        curdir = os.path.abspath(os.getcwd())
        try:
            render_templates(*all_files_by_mask('*.mint'), loader=loader)
            print 'Monitoring for file changes...'
            for changed_file in iter_changed():
                print 'Changes in file: ', changed_file, datetime.datetime.now().strftime('%H:%M:%S')
                render_templates(changed_file, loader=loader)
        except KeyboardInterrupt:
            pass
    else:
        print 'Try --help'
