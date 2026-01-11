# Chunk: aa0c0ef3fca8_2

- source: `.venv-lab/Lib/site-packages/lark/tree.py`
- lines: 173-260
- chunk: 3/4

```
s the given data."""
        return self.find_pred(lambda t: t.data == data)

###}

    def find_token(self, token_type: str) -> Iterator[_Leaf_T]:
        """Returns all tokens whose type equals the given token_type.

        This is a recursive function that will find tokens in all the subtrees.

        Example:
            >>> term_tokens = tree.find_token('TERM')
        """
        return self.scan_values(lambda v: isinstance(v, Token) and v.type == token_type)

    def expand_kids_by_data(self, *data_values):
        """Expand (inline) children with any of the given data values. Returns True if anything changed"""
        changed = False
        for i in range(len(self.children)-1, -1, -1):
            child = self.children[i]
            if isinstance(child, Tree) and child.data in data_values:
                self.children[i:i+1] = child.children
                changed = True
        return changed


    def scan_values(self, pred: 'Callable[[Branch[_Leaf_T]], bool]') -> Iterator[_Leaf_T]:
        """Return all values in the tree that evaluate pred(value) as true.

        This can be used to find all the tokens in the tree.

        Example:
            >>> all_tokens = tree.scan_values(lambda v: isinstance(v, Token))
        """
        for c in self.children:
            if isinstance(c, Tree):
                for t in c.scan_values(pred):
                    yield t
            else:
                if pred(c):
                    yield c

    def __deepcopy__(self, memo):
        return type(self)(self.data, deepcopy(self.children, memo), meta=self._meta)

    def copy(self) -> 'Tree[_Leaf_T]':
        return type(self)(self.data, self.children)

    def set(self, data: str, children: 'List[Branch[_Leaf_T]]') -> None:
        self.data = data
        self.children = children


ParseTree = Tree['Token']


class SlottedTree(Tree):
    __slots__ = 'data', 'children', 'rule', '_meta'


def pydot__tree_to_png(tree: Tree, filename: str, rankdir: 'Literal["TB", "LR", "BT", "RL"]'="LR", **kwargs) -> None:
    graph = pydot__tree_to_graph(tree, rankdir, **kwargs)
    graph.write_png(filename)


def pydot__tree_to_dot(tree: Tree, filename, rankdir="LR", **kwargs):
    graph = pydot__tree_to_graph(tree, rankdir, **kwargs)
    graph.write(filename)


def pydot__tree_to_graph(tree: Tree, rankdir="LR", **kwargs):
    """Creates a colorful image that represents the tree (data+children, without meta)

    Possible values for `rankdir` are "TB", "LR", "BT", "RL", corresponding to
    directed graphs drawn from top to bottom, from left to right, from bottom to
    top, and from right to left, respectively.

    `kwargs` can be any graph attribute (e. g. `dpi=200`). For a list of
    possible attributes, see https://www.graphviz.org/doc/info/attrs.html.
    """

    import pydot  # type: ignore[import-not-found]
    graph = pydot.Dot(graph_type='digraph', rankdir=rankdir, **kwargs)

    i = [0]

    def new_leaf(leaf):
```
