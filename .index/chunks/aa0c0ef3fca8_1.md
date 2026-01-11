# Chunk: aa0c0ef3fca8_1

- source: `.venv-lab/Lib/site-packages/lark/tree.py`
- lines: 88-183
- chunk: 2/4

```
n'

    def pretty(self, indent_str: str='  ') -> str:
        """Returns an indented string representation of the tree.

        Great for debugging.
        """
        return ''.join(self._pretty(0, indent_str))

    def __rich__(self, parent:Optional['rich.tree.Tree']=None) -> 'rich.tree.Tree':
        """Returns a tree widget for the 'rich' library.

        Example:
            ::
                from rich import print
                from lark import Tree

                tree = Tree('root', ['node1', 'node2'])
                print(tree)
        """
        return self._rich(parent)

    def _rich(self, parent):
        if parent:
            tree = parent.add(f'[bold]{self.data}[/bold]')
        else:
            import rich.tree
            tree = rich.tree.Tree(self.data)

        for c in self.children:
            if isinstance(c, Tree):
                c._rich(tree)
            else:
                tree.add(f'[green]{c}[/green]')

        return tree

    def __eq__(self, other):
        try:
            return self.data == other.data and self.children == other.children
        except AttributeError:
            return False

    def __ne__(self, other):
        return not (self == other)

    def __hash__(self) -> int:
        return hash((self.data, tuple(self.children)))

    def iter_subtrees(self) -> 'Iterator[Tree[_Leaf_T]]':
        """Depth-first iteration.

        Iterates over all the subtrees, never returning to the same node twice (Lark's parse-tree is actually a DAG).
        """
        queue = [self]
        subtrees = dict()
        for subtree in queue:
            subtrees[id(subtree)] = subtree
            queue += [c for c in reversed(subtree.children)
                      if isinstance(c, Tree) and id(c) not in subtrees]

        del queue
        return reversed(list(subtrees.values()))

    def iter_subtrees_topdown(self):
        """Breadth-first iteration.

        Iterates over all the subtrees, return nodes in order like pretty() does.
        """
        stack = [self]
        stack_append = stack.append
        stack_pop = stack.pop
        while stack:
            node = stack_pop()
            if not isinstance(node, Tree):
                continue
            yield node
            for child in reversed(node.children):
                stack_append(child)

    def find_pred(self, pred: 'Callable[[Tree[_Leaf_T]], bool]') -> 'Iterator[Tree[_Leaf_T]]':
        """Returns all nodes of the tree that evaluate pred(node) as true."""
        return filter(pred, self.iter_subtrees())

    def find_data(self, data: str) -> 'Iterator[Tree[_Leaf_T]]':
        """Returns all nodes of the tree whose data equals the given data."""
        return self.find_pred(lambda t: t.data == data)

###}

    def find_token(self, token_type: str) -> Iterator[_Leaf_T]:
        """Returns all tokens whose type equals the given token_type.

        This is a recursive function that will find tokens in all the subtrees.
```
