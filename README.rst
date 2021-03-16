Calculator
==========

`calc.py` implements a parser for a command-line calculator.

`calc_runner.py` implements a read-evaluate-print loop (`repl`) for the calculator.

`calc_test.py` are unit tests for the calculator.

The calculator recognises simple mathematical expressions, involving the four
standard binary operators, ``+``, ``-``, ``*``, and ``/``, with also parentheses and unary negation.
Normally, a the parsing would be split into stages - `tokenisation` would first split the incoming
characters into meaningful tokens, such as numbers, and operators, then `parsing` would parse the
token-stream and create a syntax tree, then the expression's value can be calculated from the
syntax tree. In this short calculator, tokenisation and calclulation of the result are done on-the-fly
during parsing.


The `language` that the calulator recognises is described by rules using EBNF
(`Extended Backus-Naur Form <https://en.wikipedia.org/wiki/Extended_Backus%E2%80%93Naur_form>`_):

::

    exp ::= term [ [ '+' | '-' ] term ]*
    term ::= factor [ [ '/' | '*' ] factor ]*
    factor ::= <number> | '(' exp ')' | '-' factor

These rules describe the calculator's expression.
Unfortunately, there are many conflicting notations for EBNF. The notation I'm using here is:

- ``[...]`` a group
- ``|`` alternative between left-side and right-side. Implemented with an ``if`` statement
- ``[...]*`` a group that can repeat zero or more times. Implemented with a ``while`` loop.
- ``<number>`` any valid number.
- ``'X'`` the character ``X``

Each rule, named by the left-hand-side of the ``::=``, becomes a Python function to implement that rule.
The rules are setup in a way that ensures that the correct operator precedence is respected. For example,
with the expression ``1+2*3``, the calculator will perform the multiplication first and give a value of 7.

First, I start off with the constructor:

.. code-block:: python

    def __init__(self):
        self.line: str = ''
        self.current: str = ''

In the constructor two variables are initialised: ``self.line``, which holds the remaining line
to be parsed, and ``self.current``, which holds the most recently recognised chunk of the line.
The result is calculated on-the-fly as the expression is parsed, so no extra variables are required.

Before I can parse, I need a function for looking at ``self.line`` and recognising the next
piece of the expression:

.. code-block:: python

    def _is_next(self, regexp: str) -> bool:
        m = re.match(r'\s*' + regexp + r'\s*', self.line)
        if m:
            self.current = m.group().strip()
            self.line = self.line[m.end():]
            return True
        return False

The technical term for this is `tokenisation` - splitting up the input characters into `tokens`.
Though here I'm doing the tokenisation on-the-fly during parsing rather than the traditional
method where it is a separate step prior to parsing.

The ``_is_next`` method takes a string representing a `regular expression
<https://docs.python.org/3/library/re.html>`_. The regular expression describes what the parser
is expecting the next matching token (or tokens) to be. The ``r'\s*'`` on each side of ``regexp``
is added to eat up any whitespace.

If the regular expression matches the start of the line, I set ``self.current`` to the piece
of string that matched the regular expression,
and I strip the part that was matched off ``self.line``. Otherwise, I return False (no match).
So ``self.current`` always contains the next matched token, and ``self.line`` always contains the remaining
input string after the match.

The entry-point for parsing a line is the `parse` method, which takes the line containing the
expression and returns the value of that expression:

.. code-block:: python

    def parse(self, expr: str) -> float:
        self.line = expr
        result = self._exp()
        if self.line != '':
            raise SyntaxError(f"Unexpected character after expression: '{self.line[0]}'")
        return result

This doesn't represent a rule in the EBNF above, but behaves like a ``parse := exp`` rule
to start the parsing, by calling the ``self._exp()`` method. I have to check there are no
unexpected characters at the end of the expression: ``1+1`` is good, but ``1+1+`` is not valid.
If there's extra characters after a valid expression, it's a syntax error.

The ``parse`` method calls the ``_exp`` method to calculate additions and subtractions:

.. code-block:: python

    def _exp(self) -> float:  # exp ::= term [ [ '+' | '-' ] term ]*
        result = self._term()
        while self._is_next('[-+]'):
            if self.current == '+':
                result += self._term()
            else:
                result -= self._term()
        return result


The code closely follows the ``exp`` rule from the EBNF. First, parse a 'term' (by calling the ``_term`` method)
and store the result.
In the EBNF rule, after the term is a zero-or-more group where the first item is either a ``+`` or a ``-``.
So I know that if the next item is either a ``+`` or a ``-`` that I'm in a repetition of the zero-or-more
group. If so, I then read the next term, and add or subtruct that from the current result.
If there is neither a ``+`` nor a ``-``, that means that this rule is finished.

For parsing and calculating multiplication and division, I use the ``_term`` method.

.. code-block:: python

    def _term(self) -> float:  # term ::= factor [ [ '/' | '*' ] factor ]*
        result = self._factor()
        while self._is_next('[*/]'):
            if self.current == '*':
                result *= self._factor()
            else:
                try:
                    result /= self._factor()
                except ZeroDivisionError:
                    result = float('NaN')  # "Not a Number"
        return result

The ``_term`` method follows the same pattern as the ``_exp`` method. The EBNF rules follow the same pattern also.
The only complicating factor here is that the user might divide by zero. One option for handling divide-by-zero is to
allow the ``ZeroDivisionError`` exception to propagate upwards. The other option is to use one of the special
floating-point representations for non-numeric values. Normally this would be ``-inf`` for negative infinity (e.g. -1/0),
``inf`` for positive infinity (e.g. 1/0), or ``nan`` (not a number) for 0/0. I take a shortcut here and just
use ``nan`` for all three.

The last rule, for numbers, parentheses, and unary negation is implemented in the ``_factor`` method:

.. code-block:: python

    def _factor(self) -> float:  # factor ::= <number> | '(' exp ')' | '-' factor
        if self._is_next(r'[0-9]*\.?[0-9]+'):
            return float(self.current) if '.' in self.current else int(self.current)
        if self._is_next('-'):
            return -self._factor()
        if self._is_next('[(]'):
            result = self._exp()
            if not self._is_next('[)]'):
                raise SyntaxError(
                    f"Expected ')' but got '{'<EOL>' if not self.line else self.line[0]}'")
            return result
        raise SyntaxError(
            f"Expected number or '(' but got '{'<EOL>' if not self.line else self.line[0]}'")

There are three tests, for the three different possibilities that are legal at this point in the parse.
The first is a number, and the regular expression in the call to ``is_next`` will match any sequence of
digits that contains an optional decimal point. I can tell if it's a float by whether a decimal point
was matched or not. I could just always assume it's a float and simply just have ``return float(self.current)``,
but it's nicer that 2 + 2 gives the integer result 4 rather than the float 4.0.
Unary minus is pretty straight-forward, as is parentheses, except for the fact that I have to ensure there
is a matching close parenthesis (")"), otherwise it's a syntax error.

Finally, there's a catch-all syntax error. Both syntax error messages are a little bit complicated by the fact
that I want to say what the offending character is that I wasn't expecting. This is usually the next
character in the line, but it could be that there `is` no next character in the line! In which case I
complain that the I got ``<EOL>`` (End-Of-Line) instead of what I was expecting.

While the ``Calculator`` class just implements the calculator, you can try out the calculator
interactively by running ``calc_runner.py``:

.. code-block:: python

    from calc import Calculator


    def repl():
        calc = Calculator()
        while True:
            line = input('> ')
            try:
                print(calc.parse(line))
            except SyntaxError as e:
                print(f'Syntax Error: {e.msg}')


    if __name__ == '__main__':
        repl()
        #bad_repl_do_not_use()  # Can do: __import__('os').system('dir')

The ``repl`` function (read-evaluate-print-loop) simply reads a line of input and then calls the calculator
to parse it, and prints the result. If the result was a syntax error, then catch that and print it instead.

All this code to implement a calculator might seem overkill when it can be done in python with a short snippet:

.. code-block:: python

    def bad_repl_do_not_use():
        while True:
            print(eval(input('> ')))


Since Python has a built-in ``eval`` function for evaluating expressions, it is possible to implement
a repl with the entire functionality of the Python expression parser,
which is much richer then my custom code to evaluate expressions. But
it is a dangerous `code-injection <https://en.wikipedia.org/wiki/Code_injection>`_ security hole,
as many statements in Python have expression counterparts. As the comment
in ``bad_repl_do_not_use`` shows, importing a library in Python can be
done `with a function <https://docs.python.org/3/library/functions.html#__import__>`_.
And if a user can import the ``os`` module, then they can
use ``os.system`` to run arbitrary commands on the computer. Not good.

Extension Ideas
---------------

* Add unary + (easy)
* Add variables (and corresponding unit tests!)
* Add some mathematical functions - sqrt, factorial, log, sin, cos etc.
* Generate `postfix representation <https://en.wikipedia.org/wiki/Reverse_Polish_notation>`_ of expression e.g. :code:`1+2*3` => :code:`123*+`
* Build an Abstract Syntax Tree, generate the corresponding Python bytecode, and execute the bytecode
