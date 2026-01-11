# Chunk: a179a3ecb1bf_7

- source: `.venv-lab/Lib/site-packages/bs4/element.py`
- lines: 541-615
- chunk: 8/45

```
e being
            concatenated.

        :param types: A tuple of NavigableString subclasses. Any
            strings of a subclass not found in this list will be
            ignored. Although there are exceptions, the default
            behavior in most cases is to consider only NavigableString
            and CData objects. That means no comments, processing
            instructions, etc.

        :return: A string.
        """
        return separator.join([s for s in self._all_strings(strip, types=types)])

    getText = get_text
    text = property(get_text)

    def replace_with(self, *args: _InsertableElement) -> Self:
        """Replace this `PageElement` with one or more other elements,
        objects, keeping the rest of the tree the same.

        :return: This `PageElement`, no longer part of the tree.
        """
        if self.parent is None:
            raise ValueError(
                "Cannot replace one element with another when the "
                "element to be replaced is not part of a tree."
            )
        if len(args) == 1 and args[0] is self:
            # Replacing an element with itself is a no-op.
            return self
        if any(x is self.parent for x in args):
            raise ValueError("Cannot replace a Tag with its parent.")
        old_parent = self.parent
        my_index = self.parent.index(self)
        self.extract(_self_index=my_index)
        for idx, replace_with in enumerate(args, start=my_index):
            old_parent.insert(idx, replace_with)
        return self

    replaceWith = _deprecated_function_alias("replaceWith", "replace_with", "4.0.0")

    def wrap(self, wrap_inside: Tag) -> Tag:
        """Wrap this `PageElement` inside a `Tag`.

        :return: ``wrap_inside``, occupying the position in the tree that used
           to be occupied by this object, and with this object now inside it.
        """
        me = self.replace_with(wrap_inside)
        wrap_inside.append(me)
        return wrap_inside

    def extract(self, _self_index: Optional[int] = None) -> Self:
        """Destructively rips this element out of the tree.

        :param _self_index: The location of this element in its parent's
           .contents, if known. Passing this in allows for a performance
           optimization.

        :return: this `PageElement`, no longer part of the tree.
        """
        if self.parent is not None:
            if _self_index is None:
                _self_index = self.parent.index(self)
            del self.parent.contents[_self_index]

        # Find the two elements that would be next to each other if
        # this element (and any children) hadn't been parsed. Connect
        # the two.
        last_child = self._last_descendant()

        # last_child can't be None because we passed accept_self=True
        # into _last_descendant. Worst case, last_child will be
        # self. Making this cast removes several mypy complaints later
```
