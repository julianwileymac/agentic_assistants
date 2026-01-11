# Chunk: 0128bbdea9ab_0

- source: `.venv-lab/Lib/site-packages/pygments/lexers/dax.py`
- lines: 1-59
- chunk: 1/3

```
"""
    pygments.lexers.dax
    ~~~~~~~~~~~~~~~~~~~

    Lexer for LilyPond.

    :copyright: Copyright 2006-2025 by the Pygments team, see AUTHORS.
    :license: BSD, see LICENSE for details.
"""

from pygments.lexer import RegexLexer, words
from pygments.token import Comment, Punctuation, Whitespace,\
    Name, Operator, String, Number, Text

__all__ = ['DaxLexer']


class DaxLexer(RegexLexer):
    """
    Lexer for Power BI DAX
    Referenced from: https://github.com/sql-bi/SyntaxHighlighterBrushDax
    """
    name = 'Dax'
    aliases = ['dax']
    filenames = ['*.dax']
    url = 'https://learn.microsoft.com/en-us/dax/dax-function-reference'
    mimetypes = []
    version_added = '2.15'

    tokens = {
        'root': [
            (r'\s+', Whitespace),
            (r"--.*\n?", Comment.Single),	# Comment: Double dash comment
            (r"//.*\n?", Comment.Single),	# Comment: Double backslash comment
            (r'/\*', Comment.Multiline, 'multiline-comments'),
            (words(('abs', 'accrint', 'accrintm', 'acos', 'acosh', 'acot', 'acoth',
                    'addcolumns', 'addmissingitems', 'all', 'allcrossfiltered',
                    'allexcept', 'allnoblankrow', 'allselected', 'amordegrc', 'amorlinc',
                    'and','approximatedistinctcount', 'asin', 'asinh', 'atan', 'atanh',
                    'average', 'averagea', 'averagex', 'beta.dist', 'beta.inv',
                    'bitand', 'bitlshift', 'bitor', 'bitrshift', 'bitxor', 'blank',
                    'calculate', 'calculatetable', 'calendar', 'calendarauto', 'ceiling',
                    'chisq.dist', 'chisq.dist.rt', 'chisq.inv', 'chisq.inv.rt',
                    'closingbalancemonth', 'closingbalancequarter', 'closingbalanceyear',
                    'coalesce', 'columnstatistics', 'combin', 'combina', 'combinevalues',
                    'concatenate', 'concatenatex', 'confidence.norm', 'confidence.t',
                    'contains', 'containsrow', 'containsstring', 'containsstringexact',
                    'convert', 'cos', 'cosh', 'cot', 'coth', 'count', 'counta', 'countax',
                    'countblank', 'countrows', 'countx', 'coupdaybs', 'coupdays',
                    'coupdaysnc', 'coupncd', 'coupnum', 'couppcd', 'crossfilter',
                    'crossjoin', 'cumipmt', 'cumprinc', 'currency', 'currentgroup',
                    'customdata', 'datatable', 'date', 'dateadd', 'datediff',
                    'datesbetween', 'datesinperiod', 'datesmtd', 'datesqtd',
                    'datesytd', 'datevalue', 'day', 'db', 'ddb', 'degrees', 'detailrows',
                    'disc', 'distinct', 'distinctcount', 'distinctcountnoblank',
                    'divide', 'dollarde', 'dollarfr', 'duration', 'earlier', 'earliest',
                    'edate', 'effect', 'endofmonth', 'endofquarter', 'endofyear',
                    'eomonth', 'error', 'evaluateandlog', 'even', 'exact', 'except',
```
