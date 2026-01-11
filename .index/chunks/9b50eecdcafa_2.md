# Chunk: 9b50eecdcafa_2

- source: `.venv-lab/Lib/site-packages/jinja2/nodes.py`
- lines: 160-237
- chunk: 3/13

```
 is None and only is None)
                or (exclude is not None and name not in exclude)
                or (only is not None and name in only)
            ):
                try:
                    yield name, getattr(self, name)
                except AttributeError:
                    pass

    def iter_child_nodes(
        self,
        exclude: t.Optional[t.Container[str]] = None,
        only: t.Optional[t.Container[str]] = None,
    ) -> t.Iterator["Node"]:
        """Iterates over all direct child nodes of the node.  This iterates
        over all fields and yields the values of they are nodes.  If the value
        of a field is a list all the nodes in that list are returned.
        """
        for _, item in self.iter_fields(exclude, only):
            if isinstance(item, list):
                for n in item:
                    if isinstance(n, Node):
                        yield n
            elif isinstance(item, Node):
                yield item

    def find(self, node_type: t.Type[_NodeBound]) -> t.Optional[_NodeBound]:
        """Find the first node of a given type.  If no such node exists the
        return value is `None`.
        """
        for result in self.find_all(node_type):
            return result

        return None

    def find_all(
        self, node_type: t.Union[t.Type[_NodeBound], t.Tuple[t.Type[_NodeBound], ...]]
    ) -> t.Iterator[_NodeBound]:
        """Find all the nodes of a given type.  If the type is a tuple,
        the check is performed for any of the tuple items.
        """
        for child in self.iter_child_nodes():
            if isinstance(child, node_type):
                yield child  # type: ignore
            yield from child.find_all(node_type)

    def set_ctx(self, ctx: str) -> "Node":
        """Reset the context of a node and all child nodes.  Per default the
        parser will all generate nodes that have a 'load' context as it's the
        most common one.  This method is used in the parser to set assignment
        targets and other nodes to a store context.
        """
        todo = deque([self])
        while todo:
            node = todo.popleft()
            if "ctx" in node.fields:
                node.ctx = ctx  # type: ignore
            todo.extend(node.iter_child_nodes())
        return self

    def set_lineno(self, lineno: int, override: bool = False) -> "Node":
        """Set the line numbers of the node and children."""
        todo = deque([self])
        while todo:
            node = todo.popleft()
            if "lineno" in node.attributes:
                if node.lineno is None or override:
                    node.lineno = lineno
            todo.extend(node.iter_child_nodes())
        return self

    def set_environment(self, environment: "Environment") -> "Node":
        """Set the environment for all nodes."""
        todo = deque([self])
        while todo:
            node = todo.popleft()
            node.environment = environment
```
