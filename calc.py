import re


class Calculator:

    def __init__(self):
        self.line: str = ''
        self.current: str = ''

    def parse(self, expr: str) -> float:
        self.line = expr
        result = self._exp()
        if self.line != '':
            raise SyntaxError(f"Unexpected character after expression: '{self.line[0]}'")
        return result

    def _exp(self) -> float:  # exp ::= term [ [ '+' | '-' ] term ]*
        result = self._term()
        while self._is_next('[-+]'):
            if self.current == '+':
                result += self._term()
            else:
                result -= self._term()
        return result

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

    def _is_next(self, regexp: str) -> bool:
        m = re.match(r'\s*' + regexp + r'\s*', self.line)
        if m:
            self.current = m.group().strip()
            self.line = self.line[m.end():]
            return True
        return False
