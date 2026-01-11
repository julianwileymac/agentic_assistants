# Chunk: f28a66f2adde_4

- source: `.venv-lab/Lib/site-packages/stack_data-0.6.3.dist-info/METADATA`
- lines: 264-321
- chunk: 5/7

```
nal raw source code of that line) is `"foo = bar"`, so `line.text[6:9]` is `"bar"`, and we want to emphasise that part by inserting HTML at positions 6 and 9 in the text. Here's how we can do that directly:

```python
markers = [
    stack_data.MarkerInLine(position=6, is_start=True, string="<b>"),
    stack_data.MarkerInLine(position=9, is_start=False, string="</b>"),
]
line.render(markers)  # returns "foo = <b>bar</b>"
```

Here `is_start=True` indicates that the marker is the first of a pair. This helps `line.render()` sort and insert the markers correctly so you don't end up with malformed HTML like `foo<b>.<i></b>bar</i>` where tags overlap.

Since we're inserting HTML, we should actually use `line.render(markers, escape_html=True)` which will escape special HTML characters in the Python source (but not the markers) so for example `foo = bar < spam` would be rendered as `foo = <b>bar</b> &lt; spam`.

Usually though you wouldn't create markers directly yourself. Instead you would start with one or more ranges and then convert them, like so:

```python
ranges = [
    stack_data.RangeInLine(start=0, end=3, data="foo"),
    stack_data.RangeInLine(start=6, end=9, data="bar"),
]

def convert_ranges(r):
    if r.data == "bar":
        return "<b>", "</b>"        

# This results in `markers` being the same as in the above example.
markers = stack_data.markers_from_ranges(ranges, convert_ranges)
```

`RangeInLine` has a `data` attribute which can be any object. `markers_from_ranges` accepts a converter function to which it passes all the `RangeInLine` objects. If the converter function returns a pair of strings, it creates two markers from them. Otherwise it should return `None` to indicate that the range should be ignored, as with the first range containing `"foo"` in this example.

The reason this is useful is because there are built in tools to create these ranges for you. For example, if we change our `print_stack()` function to contain this:

```python
def convert_variable_ranges(r):
    variable, _node = r.data
    return f'<span data-value="{repr(variable.value)}">', '</span>'

markers = stack_data.markers_from_ranges(line.variable_ranges, convert_variable_ranges)
print(f"{'-->' if line.is_current else '   '} {line.lineno:4} | {line.render(markers, escape_html=True)}")
```

Then the output becomes:

```
foo at line 15
-----------
       9 | def foo():
       (...)
      11 |     for <span data-value="4">i</span> in range(5):
      12 |         <span data-value="[]">row</span> = []
      14 |         <span data-value="[[0, 0, 0, 0, 0], [0, 1, 2, 3, 4], [0, 2, 4, 6, 8], [0, 3, 6, 9, 12], []]">result</span>.append(<span data-value="[]">row</span>)
-->   15 |         print_stack()
      17 |         for <span data-value="4">j</span> in range(5):
```
```
