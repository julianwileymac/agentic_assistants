# Chunk: 4fbdb5d9a49c_1

- source: `.venv-lab/Lib/site-packages/prompt_toolkit/completion/base.py`
- lines: 78-165
- chunk: 2/6

```
.start_position
            and self.display == other.display
            and self._display_meta == other._display_meta
        )

    def __hash__(self) -> int:
        return hash((self.text, self.start_position, self.display, self._display_meta))

    @property
    def display_text(self) -> str:
        "The 'display' field as plain text."
        from prompt_toolkit.formatted_text import fragment_list_to_text

        return fragment_list_to_text(self.display)

    @property
    def display_meta(self) -> StyleAndTextTuples:
        "Return meta-text. (This is lazy when using a callable)."
        from prompt_toolkit.formatted_text import to_formatted_text

        return to_formatted_text(self._display_meta or "")

    @property
    def display_meta_text(self) -> str:
        "The 'meta' field as plain text."
        from prompt_toolkit.formatted_text import fragment_list_to_text

        return fragment_list_to_text(self.display_meta)

    def new_completion_from_position(self, position: int) -> Completion:
        """
        (Only for internal use!)
        Get a new completion by splitting this one. Used by `Application` when
        it needs to have a list of new completions after inserting the common
        prefix.
        """
        assert position - self.start_position >= 0

        return Completion(
            text=self.text[position - self.start_position :],
            display=self.display,
            display_meta=self._display_meta,
        )


class CompleteEvent:
    """
    Event that called the completer.

    :param text_inserted: When True, it means that completions are requested
        because of a text insert. (`Buffer.complete_while_typing`.)
    :param completion_requested: When True, it means that the user explicitly
        pressed the `Tab` key in order to view the completions.

    These two flags can be used for instance to implement a completer that
    shows some completions when ``Tab`` has been pressed, but not
    automatically when the user presses a space. (Because of
    `complete_while_typing`.)
    """

    def __init__(
        self, text_inserted: bool = False, completion_requested: bool = False
    ) -> None:
        assert not (text_inserted and completion_requested)

        #: Automatic completion while typing.
        self.text_inserted = text_inserted

        #: Used explicitly requested completion by pressing 'tab'.
        self.completion_requested = completion_requested

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(text_inserted={self.text_inserted!r}, completion_requested={self.completion_requested!r})"


class Completer(metaclass=ABCMeta):
    """
    Base class for completer implementations.
    """

    @abstractmethod
    def get_completions(
        self, document: Document, complete_event: CompleteEvent
    ) -> Iterable[Completion]:
        """
        This should be a generator that yields :class:`.Completion` instances.
```
