# Chunk: f28a66f2adde_1

- source: `.venv-lab/Lib/site-packages/stack_data-0.6.3.dist-info/METADATA`
- lines: 69-144
- chunk: 2/7

```
 = inspect.currentframe().f_back
    frame_info = stack_data.FrameInfo(frame)
    print(f"{frame_info.code.co_name} at line {frame_info.lineno}")
    print("-----------")
    for line in frame_info.lines:
        print(f"{'-->' if line.is_current else '   '} {line.lineno:4} | {line.render()}")
```

(Beware that this has a major bug - it doesn't account for line gaps, which we'll learn about later)

The output of one call to `print_stack()` looks like:

```
foo at line 9
-----------
       6 | for i in range(5):
       7 |     row = []
       8 |     result.append(row)
-->    9 |     print_stack()
      10 |     for j in range(5):
```

The code for `print_stack()` is fairly self-explanatory. If you want to learn more details about a particular class or method I suggest looking through some docstrings. `FrameInfo` is a class that accepts either a frame or a traceback object and provides a bunch of nice attributes and properties (which are cached so you don't need to worry about performance). In particular `frame_info.lines` is a list of `Line` objects. `line.render()` returns the source code of that line suitable for display. Without any arguments it simply strips any common leading indentation. Later on we'll see a more powerful use for it.

You can see that `frame_info.lines` includes some lines of surrounding context. By default it includes 3 pieces of context before the main line and 1 piece after. We can configure the amount of context by passing options:

```python
options = stack_data.Options(before=1, after=0)
frame_info = stack_data.FrameInfo(frame, options)
```

Then the output looks like:

```
foo at line 9
-----------
       8 | result.append(row)
-->    9 | print_stack()
```

Note that these parameters are not the number of *lines* before and after to include, but the number of *pieces*. A piece is a range of one or more lines in a file that should logically be grouped together. A piece contains either a single simple statement or a part of a compound statement (loops, if, try/except, etc) that doesn't contain any other statements. Most pieces are a single line, but a multi-line statement or `if` condition is a single piece. In the example above, all pieces are one line, because nothing is spread across multiple lines. If we change our code to include some multiline bits:


```python
def foo():
    result = []
    for i in range(5):
        row = []
        result.append(
            row
        )
        print_stack()
        for j in range(
                5
        ):
            row.append(i * j)
    return result
```

and then run the original code with the default options, then the output is:

```
foo at line 11
-----------
       6 | for i in range(5):
       7 |     row = []
       8 |     result.append(
       9 |         row
      10 |     )
-->   11 |     print_stack()
      12 |     for j in range(
      13 |             5
      14 |     ):
```
```
