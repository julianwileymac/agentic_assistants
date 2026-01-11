# Chunk: d917abc63eda_1

- source: `.venv-lab/Lib/site-packages/attrs-25.4.0.dist-info/METADATA`
- lines: 56-150
- chunk: 2/4

```
al&utm_campaign=hynek"><img title="Tidelift" src="https://www.attrs.org/en/25.4.0/_static/sponsors/Tidelift.svg" width="190" /></a>
<a href="https://privacy-solutions.org/"><img title="Privacy Solutions" src="https://www.attrs.org/en/25.4.0/_static/sponsors/Privacy-Solutions.svg" width="190" /></a>
<a href="https://filepreviews.io/"><img title="FilePreviews" src="https://www.attrs.org/en/25.4.0/_static/sponsors/FilePreviews.svg" width="190" /></a>
<a href="https://polar.sh/"><img title="Polar" src="https://www.attrs.org/en/25.4.0/_static/sponsors/Polar.svg" width="190" /></a>
<!-- [[[end]]] -->

</p>

<!-- sponsor-break-end -->

<p align="center">
   <strong>Please consider <a href="https://github.com/sponsors/hynek">joining them</a> to help make <em>attrs</em>’s maintenance more sustainable!</strong>
</p>

<!-- teaser-end -->

## Example

*attrs* gives you a class decorator and a way to declaratively define the attributes on that class:

<!-- code-begin -->

```pycon
>>> from attrs import asdict, define, make_class, Factory

>>> @define
... class SomeClass:
...     a_number: int = 42
...     list_of_numbers: list[int] = Factory(list)
...
...     def hard_math(self, another_number):
...         return self.a_number + sum(self.list_of_numbers) * another_number


>>> sc = SomeClass(1, [1, 2, 3])
>>> sc
SomeClass(a_number=1, list_of_numbers=[1, 2, 3])

>>> sc.hard_math(3)
19
>>> sc == SomeClass(1, [1, 2, 3])
True
>>> sc != SomeClass(2, [3, 2, 1])
True

>>> asdict(sc)
{'a_number': 1, 'list_of_numbers': [1, 2, 3]}

>>> SomeClass()
SomeClass(a_number=42, list_of_numbers=[])

>>> C = make_class("C", ["a", "b"])
>>> C("foo", "bar")
C(a='foo', b='bar')
```

After *declaring* your attributes, *attrs* gives you:

- a concise and explicit overview of the class's attributes,
- a nice human-readable `__repr__`,
- equality-checking methods,
- an initializer,
- and much more,

*without* writing dull boilerplate code again and again and *without* runtime performance penalties.

---

This example uses *attrs*'s modern APIs that have been introduced in version 20.1.0, and the *attrs* package import name that has been added in version 21.3.0.
The classic APIs (`@attr.s`, `attr.ib`, plus their serious-business aliases) and the `attr` package import name will remain **indefinitely**.

Check out [*On The Core API Names*](https://www.attrs.org/en/latest/names.html) for an in-depth explanation!


### Hate Type Annotations!?

No problem!
Types are entirely **optional** with *attrs*.
Simply assign `attrs.field()` to the attributes instead of annotating them with types:

```python
from attrs import define, field

@define
class SomeClass:
    a_number = field(default=42)
    list_of_numbers = field(factory=list)
```


## Data Classes

On the tin, *attrs* might remind you of `dataclasses` (and indeed, `dataclasses` [are a descendant](https://hynek.me/articles/import-attrs/) of *attrs*).
In practice it does a lot more and is more flexible.
```
