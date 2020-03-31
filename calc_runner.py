from calc import Calculator


def repl():
    calc = Calculator()
    while True:
        line = input('> ')
        try:
            print(calc.parse(line))
        except SyntaxError as e:
            print(f'Syntax Error: {e.msg}')


def bad_repl_do_not_use():
    while True:
        print(eval(input('> ')))


if __name__ == '__main__':
    repl()
    #bad_repl_do_not_use()  # Can do: __import__('os').system('dir')
