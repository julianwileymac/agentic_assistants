# Chunk: aa0c0ef3fca8_0

- source: `.venv-lab/Lib/site-packages/lark/tree.py`
- lines: 1-98
- chunk: 1/4

```
import sys
from copy import deepcopy

from typing import List, Callable, Iterator, Union, Optional, Generic, TypeVar, TYPE_CHECKING

from .lexer import Token

if TYPE_CHECKING:
    from .lexer import TerminalDef
    try:
        import rich
    except ImportError:
        pass
    from typing import Literal

###{standalone

class Meta:

    empty: bool
    line: int
    column: int
    start_pos: int
    end_line: int
    end_column: int
    end_pos: int
    orig_expansion: 'List[TerminalDef]'
    match_tree: bool

    def __init__(self):
        self.empty = True


_Leaf_T = TypeVar("_Leaf_T")
Branch = Union[_Leaf_T, 'Tree[_Leaf_T]']


class Tree(Generic[_Leaf_T]):
    """The main tree class.

    Creates a new tree, and stores "data" and "children" in attributes of the same name.
    Trees can be hashed and compared.

    Parameters:
        data: The name of the rule or alias
        children: List of matched sub-rules and terminals
        meta: Line & Column numbers (if ``propagate_positions`` is enabled).
            meta attributes: (line, column, end_line, end_column, start_pos, end_pos,
                              container_line, container_column, container_end_line, container_end_column)
            container_* attributes consider all symbols, including those that have been inlined in the tree.
            For example, in the rule 'a: _A B _C', the regular attributes will mark the start and end of B,
            but the container_* attributes will also include _A and _C in the range. However, rules that
            contain 'a' will consider it in full, including _A and _C for all attributes.
    """

    data: str
    children: 'List[Branch[_Leaf_T]]'

    def __init__(self, data: str, children: 'List[Branch[_Leaf_T]]', meta: Optional[Meta]=None) -> None:
        self.data = data
        self.children = children
        self._meta = meta

    @property
    def meta(self) -> Meta:
        if self._meta is None:
            self._meta = Meta()
        return self._meta

    def __repr__(self):
        return 'Tree(%r, %r)' % (self.data, self.children)

    __match_args__ = ("data", "children")

    def _pretty_label(self):
        return self.data

    def _pretty(self, level, indent_str):
        yield f'{indent_str*level}{self._pretty_label()}'
        if len(self.children) == 1 and not isinstance(self.children[0], Tree):
            yield f'\t{self.children[0]}\n'
        else:
            yield '\n'
            for n in self.children:
                if isinstance(n, Tree):
                    yield from n._pretty(level+1, indent_str)
                else:
                    yield f'{indent_str*(level+1)}{n}\n'

    def pretty(self, indent_str: str='  ') -> str:
        """Returns an indented string representation of the tree.

        Great for debugging.
        """
        return ''.join(self._pretty(0, indent_str))

    def __rich__(self, parent:Optional['rich.tree.Tree']=None) -> 'rich.tree.Tree':
```
