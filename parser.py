import itertools

from tokens import *
from nodes import *
from markup import Markup

class RecursiveStack(object):
    'Stack of stacks'
    def __init__(self):
        self.stacks = [[]]

    @property
    def stack(self):
        return self.stacks[-1]

    @property
    def current(self):
        return self.stack and self.stack[-1] or None

    def push(self, item):
        self.stack.append(item)
        return True

    def pop(self):
        return self.stack.pop()
        return True

    def push_stack(self, new_stack):
        self.stacks.append(new_stack)

    def pop_stack(self):
        return self.stacks.pop()

    def __nonzero__(self):
        return len(self.stacks)

    def __repr__(self):
        return repr(self.stacks)

    def __iter__(self):
        return reversed(self.stack[:])


class Parser(object):
    def __init__(self, states):
        self.states = dict(states)

    def parse(self, tokens_stream, stack):
        current_state = 'start'
        variantes = self.states[current_state]
        for tok in tokens_stream:
            token, tok_value, lineno, pos = tok

            # accept new token
            new_state = None
            for item in variantes:
                variante, state, callback = item
                # tokens sequence
                if isinstance(variante, basestring):
                    variante = globals().get(variante)
                if isinstance(variante, (list, tuple)):
                    if token in variante:
                        new_state = state
                        break
                elif variante is token:
                    new_state = state
                    break
                elif isinstance(variante, Parser):
                    variante.parse(itertools.chain([tok], tokens_stream), stack)
                    new_state = state
                    #NOTE: tok still points to first token

            if new_state is None:
                raise WrongToken('[%s] Unexpected token "%s(%r)" at line %d, pos %d' \
                        % (current_state, token, tok_value, lineno, pos))
            # process of new_state
            elif new_state != current_state:
                if new_state == 'end':
                    #print current_state, '%s(%r)' % (token, tok_value), new_state
                    callback(tok, stack)
                    #_print_stack(stack)
                    break
                current_state = new_state
                variantes = self.states[current_state]
            # state callback
            #print current_state, '%s(%r)' % (token, tok_value), new_state
            callback(tok, stack)
            #_print_stack(stack)


def _print_stack(s):
    print '[stack]'
    for i in s:
        print ' '*4, i
    print '[end of stack]\n'


# utils functions
def get_tokens(s):
    my_tokens = []
    while s.current and isinstance(s.current, (list, tuple)):
        my_tokens.append(s.pop())
    my_tokens.reverse()
    return my_tokens

#NOTE: Callbacks are functions that takes token and stack
skip = lambda t, s: None
push = lambda t, s: s.push(t)
pop_stack = lambda t, s: s.pop_stack()
def push_stack(t, s):
    if isinstance(s.current, ElseStmtNode):
        stmt = s.pop()
        s.push_stack(stmt.body)
    elif isinstance(s.current, IfStmtNode) and s.current.orelse:
        s.push_stack(s.current.orelse[-1].body)
    else:
        if not hasattr(s.current, 'body'):
            raise SyntaxError('Unexpected indent at line %d' % t[2])
        s.push_stack(s.current.body)


# text data and inline python expressions
def py_expr(t, s):
    my_tokens = get_tokens(s)
    lineno, col_offset = my_tokens[0][2], my_tokens[0][3] - 2
    s.push(ExpressionNode(u''.join([t[1] for t in my_tokens]),
                                lineno=lineno, col_offset=col_offset))

def text_value(t, s):
    my_tokens = get_tokens(s)
    if my_tokens:
        lineno, col_offset = my_tokens[0][2], my_tokens[0][3]
        s.push(TextNode(u''.join([t[1] for t in my_tokens]),
                        lineno=lineno, col_offset=col_offset))

def text_value_with_last(t, s):
    s.push(t)
    text_value(t, s)

# parser of attribute value
attr_data_parser = Parser((
    # state name
    ('start', (
        # variantes (token, new_state, callback)
        #           ((token, token,...), new_state, callback)
        #           (other_parser, new_state, callback)
        #           ('other_parser', new_state, callback)
        (TOKEN_EXPRESSION_START, 'expr', text_value),
        (TOKEN_PARENTHESES_CLOSE, 'end', text_value),
        (all_except(TOKEN_NEWLINE), 'start', push),
        )),
    ('expr', (
        (TOKEN_EXPRESSION_END, 'start', py_expr),
        (all_tokens, 'expr', push),
        )),
))


# parser of text data and inline python expressions
data_parser = Parser((
    ('start', (
        (TOKEN_EXPRESSION_START, 'expr', text_value),
        (TOKEN_NEWLINE, 'end', text_value_with_last),
        (all_except(TOKEN_INDENT), 'start', push),
        )),
    ('expr', (
        (TOKEN_EXPRESSION_END, 'start', py_expr),
        (all_tokens, 'expr', push),
        )),
    ('short_expr', (
        (TOKEN_NEWLINE, 'start', py_expr),
        (all_tokens, 'expr', push),
        )),
))


# tag and tag attributes callbacks
def tag_name(t, s):
    #if isinstance(s.current, (list, tuple)):
    my_tokens = get_tokens(s)
    if my_tokens:
        lineno, col_offset = my_tokens[0][2], my_tokens[0][3] - 1
        s.push(TagNode(u''.join([t[1] for t in my_tokens]),
                       lineno=lineno, col_offset=col_offset))

def tag_attr_name(t, s):
    my_tokens = get_tokens(s)
    lineno, col_offset = my_tokens[0][2], my_tokens[0][3]
    s.push(TagAttrNode(u''.join([t[1] for t in my_tokens]),
                       lineno=lineno, col_offset=col_offset))

def tag_attr_value(t, s):
    nodes = []
    while not isinstance(s.current, TagAttrNode):
        nodes.append(s.pop())
    attr = s.current
    nodes.reverse()
    attr.value = nodes

def set_attr(t, s):
    nodes = []
    while not isinstance(s.current, TagAttrNode):
        nodes.append(s.pop())
    attr = s.pop()
    nodes.reverse()
    attr.value = nodes
    s.push(SetAttrNode(attr))

def append_attr(t, s):
    nodes = []
    while not isinstance(s.current, TagAttrNode):
        nodes.append(s.pop())
    attr = s.pop()
    nodes.reverse()
    attr.value = nodes
    s.push(AppendAttrNode(attr))

def tag_node(t, s):
    attrs = []
    while isinstance(s.current, TagAttrNode):
        attrs.append(s.pop())
    tag = s.pop()
    # if there were no attrs
    if isinstance(tag, (list, tuple)):
        my_tokens = get_tokens(s)
        my_tokens.append(tag)
        lineno, col_offset = my_tokens[0][2], my_tokens[0][3] - 1
        tag = TagNode(u''.join([t[1] for t in my_tokens]),
                      lineno=lineno, col_offset=col_offset)
    if attrs:
        tag.attrs = attrs
    s.push(tag)

def tag_node_with_data(t, s):
    tag_node(t, s)
    push_stack(t, s)

# tag parser
tag_parser = Parser((
    ('start', (
        (TOKEN_TEXT, 'start', push),
        (TOKEN_MINUS, 'start', push),
        (TOKEN_COLON, 'start', push),
        (TOKEN_DOT, 'attr', tag_name),
        (TOKEN_WHITESPACE, 'continue', tag_node_with_data),
        (TOKEN_SHORT_EXPRESSION, 'evaluate', tag_node_with_data),
        (TOKEN_NEWLINE, 'end', tag_node),
        )),
    ('attr', (
        (TOKEN_TEXT, 'attr', push),
        (TOKEN_MINUS, 'attr', push),
        (TOKEN_COLON, 'attr', push),
        (TOKEN_PARENTHESES_OPEN, 'attr_value', tag_attr_name),
        )),
    ('attr_value', (
        (attr_data_parser, 'start', tag_attr_value),
        )),
    ('continue', (
        (TOKEN_TAG_START, 'nested_tag', skip),
        (TOKEN_NEWLINE, 'end', pop_stack),
        (data_parser, 'end', pop_stack),
        )),
    ('nested_tag', (
        ('nested_tag_parser', 'end', pop_stack),
        )),
    ('evaluate', (
        (TOKEN_NEWLINE, 'end', pop_stack),
        (data_parser, 'end', pop_stack),
        )),
))


# this is modified tag parser, supports inline tags with data
nested_tag_parser = Parser(dict(tag_parser.states, start=(
        (TOKEN_TEXT, 'start', push),
        (TOKEN_MINUS, 'start', push),
        (TOKEN_COLON, 'start', push),
        (TOKEN_DOT, 'attr', tag_name),
        (TOKEN_WHITESPACE, 'continue', tag_node_with_data),
        (TOKEN_NEWLINE, 'end', tag_node),
        )
).iteritems())


# base parser callbacks
def base_template(t, s):
    my_tokens = get_tokens(s)
    lineno, col_offset = my_tokens[0][2], my_tokens[0][3]
    s.push(BaseTemplate(u''.join([t[1] for t in my_tokens])))

def html_comment(t, s):
    my_tokens = get_tokens(s)
    lineno, col_offset = my_tokens[0][2], my_tokens[0][3]
    s.push(TextNode(Markup(u'<!-- %s -->' % (u''.join([t[1] for t in my_tokens])).strip()),
                       lineno=lineno, col_offset=col_offset))

def for_stmt(t, s):
    my_tokens = get_tokens(s)
    lineno, col_offset = my_tokens[0][2], my_tokens[0][3]
    s.push(ForStmtNode(u''.join([t[1] for t in my_tokens]),
                       lineno=lineno, col_offset=col_offset))

def if_stmt(t, s):
    my_tokens = get_tokens(s)
    lineno, col_offset = my_tokens[0][2], my_tokens[0][3]
    s.push(IfStmtNode(u''.join([t[1] for t in my_tokens]),
                       lineno=lineno, col_offset=col_offset))

def elif_stmt(t, s):
    if not isinstance(s.current, IfStmtNode):
        pass
        #XXX: raise TemplateError
    my_tokens = get_tokens(s)
    lineno, col_offset = my_tokens[0][2], my_tokens[0][3]
    stmt = IfStmtNode(u''.join([t[1] for t in my_tokens]),
                       lineno=lineno, col_offset=col_offset)
    s.current.orelse.append(stmt)

def else_stmt(t, s):
    lineno, col_offset = t[2], t[3] - 6
    if not isinstance(s.current, IfStmtNode):
        pass
        #XXX: raise TemplateError
    stmt = ElseStmtNode(lineno=lineno, col_offset=col_offset)
    # elif
    if s.current.orelse:
        s.current.orelse[-1].orelse.append(stmt)
    # just else
    else:
        s.current.orelse.append(stmt)
    s.push(stmt)

def slot_def(t, s):
    my_tokens = get_tokens(s)
    lineno, col_offset = my_tokens[0][2], my_tokens[0][3]
    s.push(SlotDefNode(u''.join([t[1] for t in my_tokens]),
                       lineno=lineno, col_offset=col_offset))

def slot_call(t, s):
    my_tokens = get_tokens(s)
    lineno, col_offset = my_tokens[0][2], my_tokens[0][3]
    s.push(SlotCallNode(u''.join([t[1] for t in my_tokens]),
                       lineno=lineno, col_offset=col_offset))

# base parser (MAIN PARSER)
block_parser = Parser((
    # start is always the start of a new line
    ('start', (
        (TOKEN_TEXT, 'text', push),
        (TOKEN_EXPRESSION_START, 'expr', skip),
        (TOKEN_TAG_ATTR_SET, 'set_attr', skip),
        (TOKEN_TAG_ATTR_APPEND, 'append_attr', skip),
        (TOKEN_TAG_START, 'tag', skip),
        (TOKEN_STATEMENT_FOR, 'for_stmt', push),
        (TOKEN_STATEMENT_IF, 'if_stmt', push),
        (TOKEN_STATEMENT_ELIF, 'elif_stmt', push),
        (TOKEN_STATEMENT_ELSE, 'else_stmt', skip),
        (TOKEN_SLOT_DEF, 'slot_def', push),
        (TOKEN_BASE_TEMPLATE, 'base', skip),
        (TOKEN_STMT_CHAR, 'slot_call', skip),
        (TOKEN_COMMENT, 'comment', skip),
        (TOKEN_BACKSLASH, 'escaped_text', skip),
        (TOKEN_INDENT, 'indent', push_stack),
        (TOKEN_UNINDENT, 'start', pop_stack),
        (TOKEN_NEWLINE, 'start', skip),
        (TOKEN_EOF, 'end', skip),
        (all_tokens, 'text', push),
        )),
    # to prevent multiple indentions in a row
    ('indent', (
        (TOKEN_TEXT, 'text', push),
        (TOKEN_EXPRESSION_START, 'expr', skip),
        (TOKEN_TAG_ATTR_APPEND, 'append_attr', skip),
        (TOKEN_TAG_ATTR_SET, 'set_attr', skip),
        (TOKEN_TAG_START, 'tag', skip),
        (TOKEN_STATEMENT_FOR, 'for_stmt', push),
        (TOKEN_STATEMENT_IF, 'if_stmt', push),
        (TOKEN_STATEMENT_ELIF, 'elif_stmt', push),
        (TOKEN_STATEMENT_ELSE, 'else_stmt', skip),
        (TOKEN_SLOT_DEF, 'slot_def', push),
        (TOKEN_STMT_CHAR, 'slot_call', skip),
        (TOKEN_COMMENT, 'comment', skip),
        (TOKEN_BACKSLASH, 'escaped_text', skip),
        (TOKEN_NEWLINE, 'start', skip),
        (TOKEN_UNINDENT, 'start', pop_stack),
        )),
    ('base', (
        (TOKEN_NEWLINE, 'start', base_template),
        (all_tokens, 'base', push),
        )),
    ('text', (
        (TOKEN_EXPRESSION_START, 'expr', text_value),
        (TOKEN_NEWLINE, 'start', text_value_with_last),
        (all_except(TOKEN_INDENT), 'text', push),
        )),
    ('expr', (
        (TOKEN_EXPRESSION_END, 'text', py_expr),
        (all_tokens, 'expr', push),
        )),
    ('escaped_text', (
        (TOKEN_NEWLINE, 'start', text_value_with_last),
        (all_except(TOKEN_INDENT), 'escaped_text', push),
        )),
    ('tag', (
        (tag_parser, 'start', skip),
        )),
    ('comment', (
        (TOKEN_NEWLINE, 'start', html_comment),
        (all_tokens, 'comment', push),
        )),
    ('set_attr', (
        (TOKEN_TEXT, 'set_attr', push),
        (TOKEN_MINUS, 'set_attr', push),
        (TOKEN_COLON, 'set_attr', push),
        (TOKEN_PARENTHESES_OPEN, 'set_attr_value', tag_attr_name),
        )),
    ('set_attr_value', (
        (attr_data_parser, 'start', set_attr),
        )),
    ('append_attr', (
        (TOKEN_TEXT, 'append_attr', push),
        (TOKEN_MINUS, 'append_attr', push),
        (TOKEN_COLON, 'append_attr', push),
        (TOKEN_PARENTHESES_OPEN, 'append_attr_value', tag_attr_name),
        )),
    ('append_attr_value', (
        (attr_data_parser, 'start', append_attr),
        )),
    ('for_stmt', (
        (TOKEN_NEWLINE, 'start', for_stmt),
        (all_tokens, 'for_stmt', push),
        )),
    ('if_stmt', (
        (TOKEN_NEWLINE, 'start', if_stmt),
        (all_tokens, 'if_stmt', push),
        )),
    ('elif_stmt', (
        (TOKEN_NEWLINE, 'start', elif_stmt),
        (all_tokens, 'elif_stmt', push),
        )),
    ('else_stmt', (
        (TOKEN_NEWLINE, 'start', else_stmt),
        #(all_tokens, 'else_stmt', push),
        )),
    ('slot_def', (
        (TOKEN_NEWLINE, 'start', slot_def),
        (all_tokens, 'slot_def', push),
        )),
    ('slot_call', (
        (TOKEN_NEWLINE, 'start', slot_call),
        (all_tokens, 'slot_call', push),
        )),
))
