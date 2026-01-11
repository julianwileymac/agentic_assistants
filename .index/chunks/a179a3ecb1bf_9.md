# Chunk: a179a3ecb1bf_9

- source: `.venv-lab/Lib/site-packages/bs4/element.py`
- lines: 673-754
- chunk: 10/45

```
ing
        or an empty Tag.

        :param is_initialized: Has `PageElement.setup` been called on
            this `PageElement` yet?

        :param accept_self: Is ``self`` an acceptable answer to the
            question?
        """
        if is_initialized and self.next_sibling is not None:
            last_child = self.next_sibling.previous_element
        else:
            last_child = self
            while isinstance(last_child, Tag) and last_child.contents:
                last_child = last_child.contents[-1]
        if not accept_self and last_child is self:
            last_child = None
        return last_child

    _lastRecursiveChild = _deprecated_alias(
        "_lastRecursiveChild", "_last_descendant", "4.0.0"
    )

    def insert_before(self, *args: _InsertableElement) -> List[PageElement]:
        """Makes the given element(s) the immediate predecessor of this one.

        All the elements will have the same `PageElement.parent` as
        this one, and the given elements will occur immediately before
        this one.

        :param args: One or more PageElements.

        :return The list of PageElements that were inserted.
        """
        parent = self.parent
        if parent is None:
            raise ValueError("Element has no parent, so 'before' has no meaning.")
        if any(x is self for x in args):
            raise ValueError("Can't insert an element before itself.")
        results: List[PageElement] = []
        for predecessor in args:
            # Extract first so that the index won't be screwed up if they
            # are siblings.
            if isinstance(predecessor, PageElement):
                predecessor.extract()
            index = parent.index(self)
            results.extend(parent.insert(index, predecessor))

        return results

    def insert_after(self, *args: _InsertableElement) -> List[PageElement]:
        """Makes the given element(s) the immediate successor of this one.

        The elements will have the same `PageElement.parent` as this
        one, and the given elements will occur immediately after this
        one.

        :param args: One or more PageElements.

        :return The list of PageElements that were inserted.
        """
        # Do all error checking before modifying the tree.
        parent = self.parent
        if parent is None:
            raise ValueError("Element has no parent, so 'after' has no meaning.")
        if any(x is self for x in args):
            raise ValueError("Can't insert an element after itself.")

        offset = 0
        results: List[PageElement] = []
        for successor in args:
            # Extract first so that the index won't be screwed up if they
            # are siblings.
            if isinstance(successor, PageElement):
                successor.extract()
            index = parent.index(self)
            results.extend(parent.insert(index + 1 + offset, successor))
            offset += 1

        return results
```
