# Chunk: a179a3ecb1bf_8

- source: `.venv-lab/Lib/site-packages/bs4/element.py`
- lines: 608-683
- chunk: 9/45

```
) hadn't been parsed. Connect
        # the two.
        last_child = self._last_descendant()

        # last_child can't be None because we passed accept_self=True
        # into _last_descendant. Worst case, last_child will be
        # self. Making this cast removes several mypy complaints later
        # on as we manipulate last_child.
        last_child = cast(PageElement, last_child)
        next_element = last_child.next_element

        if self.previous_element is not None:
            if self.previous_element is not next_element:
                self.previous_element.next_element = next_element
        if next_element is not None and next_element is not self.previous_element:
            next_element.previous_element = self.previous_element
        self.previous_element = None
        last_child.next_element = None

        self.parent = None
        if (
            self.previous_sibling is not None
            and self.previous_sibling is not self.next_sibling
        ):
            self.previous_sibling.next_sibling = self.next_sibling
        if (
            self.next_sibling is not None
            and self.next_sibling is not self.previous_sibling
        ):
            self.next_sibling.previous_sibling = self.previous_sibling
        self.previous_sibling = self.next_sibling = None
        return self

    def decompose(self) -> None:
        """Recursively destroys this `PageElement` and its children.

        The element will be removed from the tree and wiped out; so
        will everything beneath it.

        The behavior of a decomposed `PageElement` is undefined and you
        should never use one for anything, but if you need to *check*
        whether an element has been decomposed, you can use the
        `PageElement.decomposed` property.
        """
        self.extract()
        e: _AtMostOneElement = self
        next_up: _AtMostOneElement = None
        while e is not None:
            next_up = e.next_element
            e.__dict__.clear()
            if isinstance(e, Tag):
                e.name = ""
                e.contents = []
            e._decomposed = True
            e = next_up

    def _last_descendant(
        self, is_initialized: bool = True, accept_self: bool = True
    ) -> _AtMostOneElement:
        """Finds the last element beneath this object to be parsed.

        Special note to help you figure things out if your type
        checking is tripped up by the fact that this method returns
        _AtMostOneElement instead of PageElement: the only time
        this method returns None is if `accept_self` is False and the
        `PageElement` has no children--either it's a NavigableString
        or an empty Tag.

        :param is_initialized: Has `PageElement.setup` been called on
            this `PageElement` yet?

        :param accept_self: Is ``self`` an acceptable answer to the
            question?
        """
        if is_initialized and self.next_sibling is not None:
```
