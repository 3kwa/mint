import ast
import htmlentitydefs
import os

from ast import Load, Store, Param
from functools import partial

from nodes import TextNode, ExpressionNode, TagAttrNode

TREE_BUILDER = '__MINT_TREE_BUILDER__'
TREE_FACTORY = '__MINT_TREE_FACTORY__'
MAIN_FUNCTION = '__MINT_MAIN__'
TAG_START = '__MINT_TAG_START__'
TAG_END = '__MINT_TAG_END__'
DATA = '__MINT_DATA__'
ESCAPE_HELLPER = '__MINT_ESCAPE__'
CURRENT_NODE = '__MINT_CURRENT_NODE__'

UNSAFE_CHARS = '&<>"'
CHARS_ENTITIES = dict([(v, '&%s;' % k) for k, v in htmlentitydefs.entitydefs.items()])
UNSAFE_CHARS_ENTITIES = [(k, CHARS_ENTITIES[k]) for k in UNSAFE_CHARS]
UNSAFE_CHARS_ENTITIES_IN_ATTR = [(k, CHARS_ENTITIES[k]) for k in '<>"']
UNSAFE_CHARS_ENTITIES.append(("'",'&#39;'))
UNSAFE_CHARS_ENTITIES_IN_ATTR.append(("'",'&#39;'))
UNSAFE_CHARS_ENTITIES_REVERSED = [(v,k) for k,v in UNSAFE_CHARS_ENTITIES]

def escape(obj, ctx='tag'):
    if hasattr(obj, '__html__'):
        safe_markup = obj.__html__()
        if ctx == 'tag':
            return safe_markup
        else:
            for k, v in UNSAFE_CHARS_ENTITIES_IN_ATTR:
                safe_markup = safe_markup.replace(k, v)
            return safe_markup
    obj = unicode(obj)
    for k, v in UNSAFE_CHARS_ENTITIES:
        obj = obj.replace(k, v)
    return obj

class AstWrapper(object):
    def __init__(self, lineno, col_offset):
        assert lineno is not None and col_offset is not None
        self.lineno = lineno
        self.col_offset = col_offset
    def __getattr__(self, name):
        attr = getattr(ast, name)
        return partial(attr, lineno=self.lineno, col_offset=self.col_offset, ctx=Load())


class MintToPythonTransformer(ast.NodeTransformer):

    def visit_MintTemplate(self, node):
        ast_ = AstWrapper(1,1)
        module = ast_.Module(body=[
            ast_.FunctionDef(name=MAIN_FUNCTION,
                             body=[],
                             args=ast_.arguments(args=[], vararg=None, kwargs=None, defaults=[]),
                             decorator_list=[])])
        body = module.body[0].body
        for n in node.body:
            result = self.visit(n)
            if isinstance(result, (list, tuple)):
                for i in result:
                    body.append(i)
            else:
                body.append(result)
        return module

    def visit_TextNode(self, node):
        ast_ = AstWrapper(node.lineno, node.col_offset)
        return ast_.Expr(value=ast_.Call(func=ast_.Name(id=DATA),
                                         args=[self.get_value(node, ast_)],
                                         keywords=[], starargs=None, kwargs=None))

    def visit_ExpressionNode(self, node):
        ast_ = AstWrapper(node.lineno, node.col_offset)
        return ast_.Expr(value=ast_.Call(func=ast_.Name(id=DATA),
                                         args=[self.get_value(node, ast_)],
                                         keywords=[], starargs=None, kwargs=None))

    def visit_SetAttrNode(self, node):
        ast_ = AstWrapper(node.attr.lineno, node.attr.col_offset)
        key, value = self.get_value(node.attr, ast_)
        return ast_.Expr(value=ast_.Call(func=ast_.Attribute(value=ast_.Name(id=CURRENT_NODE),
                                                            attr='set'),
                                        args=[key, value],
                                        keywords=[],
                                        starargs=None, kwargs=None))

    def visit_AppendAttrNode(self, node):
        ast_ = AstWrapper(node.attr.lineno, node.attr.col_offset)
        key, value = self.get_value(node.attr, ast_)
        value = ast_.BinOp(
            left=ast_.BoolOp(
                values=[ast_.Call(
                    func=ast_.Attribute(value=ast_.Name(id=CURRENT_NODE),
                                        attr='get'),
                    args=[key],
                    keywords=[],
                    starargs=None, kwargs=None), ast_.Str(s=u'')],
                op=ast.Or()),
            op=ast.Add(),
            right=value)
        return ast_.Expr(value=ast_.Call(func=ast_.Attribute(value=ast_.Name(id=CURRENT_NODE),
                                                            attr='set'),
                                        args=[key, value],
                                        keywords=[],
                                        starargs=None, kwargs=None))

    def visit_TagNode(self, node):
        ast_ = AstWrapper(node.lineno, node.col_offset)
        name = CURRENT_NODE
        attrs = ast_.Dict(keys=[], values=[])
        for a in node.attrs:
            k, v = self.get_value(a, ast_)
            attrs.keys.append(k)
            attrs.values.append(v)
        nodes = []
        # tag start
        node_start = ast_.Assign(targets=[ast_.Name(id=name, ctx=Store())],
                           value=ast_.Call(func=ast_.Name(id=TAG_START),
                                           args=[ast_.Str(s=escape(node.name)), attrs],
                                           keywords=[], starargs=None, kwargs=None))
        nodes.append(node_start)
        for n in node.body:
            result = self.visit(n)
            if isinstance(result, (list, tuple)):
                for i in result:
                    nodes.append(i)
            else:
                nodes.append(result)
        # tag end
        node_end = ast_.Expr(value=ast_.Call(func=ast_.Name(id=TAG_END),
                                             args=[ast_.Str(s=escape(node.name))],
                                             keywords=[], starargs=None, kwargs=None))
        nodes.append(node_end)
        return nodes

    def visit_ForStmtNode(self, node):
        ast_ = AstWrapper(node.lineno, node.col_offset)
        result = []
        expr = node.text[1:]
        if not expr.endswith(':'):
            expr += ':'
        expr += 'pass'
        value = ast.parse(expr).body[0]
        for n in node.body:
            result = self.visit(n)
            if isinstance(result, (list, tuple)):
                for i in result:
                    value.body.append(i)
            else:
                value.body.append(result)
        value.lineno = ast_.lineno
        value.col_offset = ast_.col_offset
        return value

    def visit_IfStmtNode(self, node):
        ast_ = AstWrapper(node.lineno, node.col_offset)
        result = []
        expr = node.text[1:]
        if not expr.endswith(':'):
            expr += ':'
        expr += 'pass'
        if expr.startswith('el'):
            expr = expr[2:]
        value = ast.parse(expr).body[0]
        value.body = []
        value.lineno = ast_.lineno
        value.col_offset = ast_.col_offset
        #XXX: if nodes is empty list raise TemplateError
        for n in node.body:
            result = self.visit(n)
            if isinstance(result, (list, tuple)):
                for i in result:
                    value.body.append(i)
            else:
                value.body.append(result)
        for n in node.orelse:
            result = self.visit(n)
            if isinstance(result, (list, tuple)):
                for i in result:
                    value.orelse.append(i)
            else:
                value.orelse.append(result)
        return value

    def visit_ElseStmtNode(self, node):
        value = []
        for n in node.body:
            result = self.visit(n)
            if isinstance(result, (list, tuple)):
                for i in result:
                    value.append(i)
            else:
                value.append(result)
        return value

    def visit_SlotDefNode(self, node):
        ast_ = AstWrapper(node.lineno, node.col_offset)
        result = []
        expr = node.text[1:]
        if not expr.endswith(':'):
            expr += ':'
        expr += 'pass'
        value = ast.parse(expr).body[0]
        value.lineno = ast_.lineno
        value.col_offset = ast_.col_offset
        #XXX: if self.nodes is empty list raise TemplateError
        for n in node.body:
            result = self.visit(n)
            if isinstance(result, (list, tuple)):
                for i in result:
                    value.body.append(i)
            else:
                value.body.append(result)
        return value

    def visit_SlotCallNode(self, node):
        ast_ = AstWrapper(node.lineno, node.col_offset)
        expr = node.text
        value = ast.parse(expr).body[0].value
        value.lineno = ast_.lineno
        value.col_offset = ast_.col_offset
        return ast_.Expr(value=ast_.Call(func=ast_.Name(id=DATA),
                                         args=[value], keywords=[]))

    def get_value(self, node, ast_, ctx='tag'):
        if isinstance(node, TextNode):
            return ast_.Str(s=escape(node.text, ctx=ctx))
        elif isinstance(node, ExpressionNode):
            expr = ast.parse(node.text).body[0].value
            return ast_.Call(func=ast_.Name(id=ESCAPE_HELLPER),
                             args=[expr],
                             keywords=[ast.keyword(arg='ctx', value=ast_.Str(s=ctx))],
                             starargs=None, kwargs=None)
        elif isinstance(node, TagAttrNode):
            key = ast_.Str(s=node.name)
            value = ast_.Str(s=u'')
            nodes = list(node.value)
            if nodes:
                value = ast_.Call(func=ast_.Attribute(value=ast_.Str(s=u''),
                                                      attr='join'),
                                  args=[ast_.Tuple(elts=[self.get_value(n, ast_, ctx='attr') for n in nodes])],
                                  keywords=[], starargs=None, kwargs=None)
            return key, value


class SlotsGetter(ast.NodeTransformer):
    'Node transformer, collects slots'
    def __init__(self):
        self.slots = {}
        self.base = None
    def visit_FunctionDef(self, node):
        ast_ = AstWrapper(node.lineno, node.col_offset)
        new_tree_call = ast_.Assign(targets=[ast_.Tuple(elts=[
                                                         ast_.Name(id=TREE_BUILDER, ctx=Store()),
                                                         ast_.Name(id=TAG_START, ctx=Store()),
                                                         ast_.Name(id=TAG_END, ctx=Store()),
                                                         ast_.Name(id=DATA, ctx=Store())],
                                                       ctx=Store())],
                                    value=ast_.Call(func=ast_.Name(id=TREE_FACTORY),
                                                    args=[],
                                                    keywords=[], starargs=None, kwargs=None))
        tree_to_unicode_call = ast_.Return(value=ast_.Call(func=ast_.Attribute(
                                                value=ast_.Name(id=TREE_BUILDER),
                                                attr='to_unicode'),
                                           args=[],
                                           keywords=[]))
        node.body.insert(0, new_tree_call)
        node.body.append(tree_to_unicode_call)
        if node.name == MAIN_FUNCTION:
            _nones = []
            for n in node.body:
                v = self.visit(n)
                if v is None:
                    _nones.append(n)
            for n in _nones:
                node.body.remove(n)
            return node
        self.slots[node.name] = node
        node.name = 'slot_' + os.urandom(5).encode('hex')
    def visit_BaseTemplate(self, node):
        self.base = node.name


