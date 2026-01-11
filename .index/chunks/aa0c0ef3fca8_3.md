# Chunk: aa0c0ef3fca8_3

- source: `.venv-lab/Lib/site-packages/lark/tree.py`
- lines: 250-282
- chunk: 4/4

```
be any graph attribute (e. g. `dpi=200`). For a list of
    possible attributes, see https://www.graphviz.org/doc/info/attrs.html.
    """

    import pydot  # type: ignore[import-not-found]
    graph = pydot.Dot(graph_type='digraph', rankdir=rankdir, **kwargs)

    i = [0]

    def new_leaf(leaf):
        node = pydot.Node(i[0], label=repr(leaf))
        i[0] += 1
        graph.add_node(node)
        return node

    def _to_pydot(subtree):
        color = hash(subtree.data) & 0xffffff
        color |= 0x808080

        subnodes = [_to_pydot(child) if isinstance(child, Tree) else new_leaf(child)
                    for child in subtree.children]
        node = pydot.Node(i[0], style="filled", fillcolor="#%x" % color, label=subtree.data)
        i[0] += 1
        graph.add_node(node)

        for subnode in subnodes:
            graph.add_edge(pydot.Edge(node, subnode))

        return node

    _to_pydot(tree)
    return graph
```
