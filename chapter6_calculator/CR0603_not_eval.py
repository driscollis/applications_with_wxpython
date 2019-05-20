# CR0603_not_eval.py

import ast
import operator

allowed_operators = {ast.Add: operator.add, ast.Sub: operator.sub,
                     ast.Mult: operator.mul, ast.Div: operator.truediv}

def noeval(expression):
    if isinstance(expression, ast.Num):
        return expression.n
    elif isinstance(expression, ast.BinOp):
        print('Operator: {}'.format(expression.op))
        print('Left operand: {}'.format(expression.left))
        print('Right operand: {}'.format(expression.right))
        op = allowed_operators.get(type(expression.op))
        if op:
            return op(noeval(expression.left),
                      noeval(expression.right))
    else:
        print('This statement will be ignored')

if __name__ == '__main__':
    print(ast.parse('1+4', mode='eval').body)
    print(noeval(ast.parse('1+4', mode='eval').body))
    print(noeval(ast.parse('1**4', mode='eval').body))
    print(noeval(ast.parse("__import__('os').remove('path/to/file')", mode='eval').body))

