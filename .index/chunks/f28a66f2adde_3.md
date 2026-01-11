# Chunk: f28a66f2adde_3

- source: `.venv-lab/Lib/site-packages/stack_data-0.6.3.dist-info/METADATA`
- lines: 199-269
- chunk: 4/7

```
 that the function signature is always showing. This can be done with `Options(include_signature=True)`. The result looks like this:

```
foo at line 14
-----------
       9 | def foo():
       (...)
      11 |     for i in range(5):
      12 |         row = []
      13 |         result.append(row)
-->   14 |         print_stack()
      15 |         for j in range(5):
```

To avoid wasting space, pieces never start or end with a blank line, and blank lines between pieces are excluded. So if our code looks like this:


```python
    for i in range(5):
        row = []

        result.append(row)
        print_stack()

        for j in range(5):
```

The output doesn't change much, except you can see jumps in the line numbers:

```
      11 |     for i in range(5):
      12 |         row = []
      14 |         result.append(row)
-->   15 |         print_stack()
      17 |         for j in range(5):
```

## Variables

You can also inspect variables and other expressions in a frame, e.g:

```python
    for var in frame_info.variables:
        print(f"{var.name} = {repr(var.value)}")
```

which may output:

```python
result = [[0, 0, 0, 0, 0], [0, 1, 2, 3, 4], [0, 2, 4, 6, 8], [0, 3, 6, 9, 12], []]
i = 4
row = []
j = 4
```

`frame_info.variables` returns a list of `Variable` objects, which have attributes `name`, `value`, and `nodes`, which is a list of all AST representing that expression.

A `Variable` may refer to an expression other than a simple variable name. It can be any expression evaluated by the library [`pure_eval`](https://github.com/alexmojaki/pure_eval) which it deems 'interesting' (see those docs for more info). This includes expressions like `foo.bar` or `foo[bar]`. In these cases `name` is the source code of that expression. `pure_eval` ensures that it only evaluates expressions that won't have any side effects, e.g. where `foo.bar` is a normal attribute rather than a descriptor such as a property.

`frame_info.variables` is a list of all the interesting expressions found in `frame_info.scope`, e.g. the current function, which may include expressions not visible in `frame_info.lines`. You can restrict the list by using `frame_info.variables_in_lines` or even `frame_info.variables_in_executing_piece`. For more control you can use `frame_info.variables_by_lineno`. See the docstrings for more information.

## Rendering lines with ranges and markers

Sometimes you may want to insert special characters into the text for display purposes, e.g. HTML or ANSI color codes. `stack_data` provides a few tools to make this easier.

Let's say we have a `Line` object where `line.text` (the original raw source code of that line) is `"foo = bar"`, so `line.text[6:9]` is `"bar"`, and we want to emphasise that part by inserting HTML at positions 6 and 9 in the text. Here's how we can do that directly:

```python
markers = [
    stack_data.MarkerInLine(position=6, is_start=True, string="<b>"),
```
