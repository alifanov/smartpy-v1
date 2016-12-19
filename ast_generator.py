import ast
import time

source_code_1 = """
class A:
    v1 = 1
"""

source_code_2 = """
class B:
    v1 = 2
    v2 = 3
"""


class ASTTranslator(object):
    node_map = {
        'ClassDef': 'class',
        'Module': 'module',
        'Assign': '=',
        'Name': 'var',
        'Num': 'num',
    }

    def walk(self, node):
        result = ()
        # print(node, dir(node))
        node_name = node.__class__.__name__
        if node_name in self.node_map:
            node_name = self.node_map[node_name]
        if node_name == 'module':
            result += (node_name, tuple((self.walk(s) for s in node.body)))
        elif node_name == 'class':
            result += (node_name, node.name, tuple((self.walk(s) for s in node.body)))
        elif node_name == '=':
            result += (node_name, self.walk(node.targets), self.walk(node.value))
        elif node_name == 'var':
            result = node.id
        elif node_name == 'num':
            result = node.n
        elif node_name == 'list':
            if len(node) == 1:
                result = self.walk(node[0])
            else:
                result = tuple((self.walk(s) for s in node))
        else:
            result += (node_name,)
        # print(node_name)
        return result


def comparable(v):
    for cls in [
        str,
        int
    ]:
        if isinstance(v, cls): return True
    return False


class ASTPatternMatcher(object):
    def get_common_expr(self, ast_list):
        # print(ast_list)
        # time.sleep(1)
        result = ''

        heads = []
        for s in ast_list:
            if s:
                heads.append(s[0])
            else:
                heads.append(())

        tails = []
        for s in ast_list:
            if s:
                tails.append(s[1:])
            else:
                tails.append(())

        # if all([isinstance(h, tuple) for h in heads]): result += '('

        if all([h == () for h in heads]): return ''
        if any([h == () for h in heads]): return ' * '

        if all([comparable(el) for el in heads]):
            if len(set(heads)) == 1:  # compare
                result += ' {} '.format(heads[0])  # return common item
            else:
                result += ' ? '  # differ
        else:
            result += '(' + self.get_common_expr(heads) + ')'

        result += self.get_common_expr(tails)
        return result


class ASTGenerator(object):
    def __init__(self, code):
        self.code = code
        self.ast = ast.parse(code)
        # print(ast.dump(self.ast))
        self.parsed_ast = ASTTranslator().walk(self.ast)[1]
        # print(self.parsed_ast)


if __name__ == "__main__":
    astg_1 = ASTGenerator(source_code_1)
    astg_2 = ASTGenerator(source_code_2)

    ast_pm = ASTPatternMatcher()
    common_expr = '({})'.format(ast_pm.get_common_expr([astg_1.parsed_ast[0], astg_2.parsed_ast[0]]))
    print(common_expr)
    match_db = {
        common_expr: [source_code_1, source_code_2]
    }

