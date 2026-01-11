# Chunk: bebb962ffad6_1

- source: `.venv-lab/Lib/site-packages/jedi/third_party/typeshed/stdlib/2and3/msilib/__init__.pyi`
- lines: 84-172
- chunk: 2/3

```
    component: Optional[str] = ...,
            feature: Optional[Feature] = ...,
            flags: Optional[int] = ...,
            keyfile: Optional[str] = ...,
            uuid: Optional[str] = ...,
        ) -> None: ...
        def make_short(self, file: str) -> str: ...
        def add_file(
            self, file: str, src: Optional[str] = ..., version: Optional[str] = ..., language: Optional[str] = ...
        ) -> str: ...
        def glob(self, pattern: str, exclude: Optional[Container[str]] = ...) -> List[str]: ...
        def remove_pyc(self) -> None: ...
    class Binary:

        name: str
        def __init__(self, fname: str) -> None: ...
        def __repr__(self) -> str: ...
    class Feature:

        id: str
        def __init__(
            self,
            db: _Database,
            id: str,
            title: str,
            desc: str,
            display: int,
            level: int = ...,
            parent: Optional[Feature] = ...,
            directory: Optional[str] = ...,
            attributes: int = ...,
        ) -> None: ...
        def set_current(self) -> None: ...
    class Control:

        dlg: Dialog
        name: str
        def __init__(self, dlg: Dialog, name: str) -> None: ...
        def event(self, event: str, argument: str, condition: str = ..., ordering: Optional[int] = ...) -> None: ...
        def mapping(self, event: str, attribute: str) -> None: ...
        def condition(self, action: str, condition: str) -> None: ...
    class RadioButtonGroup(Control):

        property: str
        index: int
        def __init__(self, dlg: Dialog, name: str, property: str) -> None: ...
        def add(self, name: str, x: int, y: int, w: int, h: int, text: str, value: Optional[str] = ...) -> None: ...
    class Dialog:

        db: _Database
        name: str
        x: int
        y: int
        w: int
        h: int
        def __init__(
            self,
            db: _Database,
            name: str,
            x: int,
            y: int,
            w: int,
            h: int,
            attr: int,
            title: str,
            first: str,
            default: str,
            cancel: str,
        ) -> None: ...
        def control(
            self,
            name: str,
            type: str,
            x: int,
            y: int,
            w: int,
            h: int,
            attr: int,
            prop: Optional[str],
            text: Optional[str],
            next: Optional[str],
            help: Optional[str],
        ) -> Control: ...
        def text(self, name: str, x: int, y: int, w: int, h: int, attr: int, text: Optional[str]) -> Control: ...
        def bitmap(self, name: str, x: int, y: int, w: int, h: int, text: Optional[str]) -> Control: ...
        def line(self, name: str, x: int, y: int, w: int, h: int) -> Control: ...
        def pushbutton(
            self, name: str, x: int, y: int, w: int, h: int, attr: int, text: Optional[str], next: Optional[str]
```
