# Chunk: f28a66f2adde_2

- source: `.venv-lab/Lib/site-packages/stack_data-0.6.3.dist-info/METADATA`
- lines: 128-209
- chunk: 3/7

```
efault options, then the output is:

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

Now lines 8-10 and lines 12-14 are each a single piece. Note that the output is essentially the same as the original in terms of the amount of code. The division of files into pieces means that the edge of the context is intuitive and doesn't crop out parts of statements or expressions. For example, if context was measured in lines instead of pieces, the last line of the above would be `for j in range(` which is much less useful.

However, if a piece is very long, including all of it could be cumbersome. For this, `Options` has a parameter `max_lines_per_piece`, which is 6 by default. Suppose we have a piece in our code that's longer than that:

```python
        row = [
            1,
            2,
            3,
            4,
            5,
        ]
```

`frame_info.lines` will truncate this piece so that instead of 7 `Line` objects it will produce 5 `Line` objects and one `LINE_GAP` in the middle, making 6 objects in total for the piece. Our code doesn't currently handle gaps, so it will raise an exception. We can modify it like so:

```python
    for line in frame_info.lines:
        if line is stack_data.LINE_GAP:
            print("       (...)")
        else:
            print(f"{'-->' if line.is_current else '   '} {line.lineno:4} | {line.render()}")
```

Now the output looks like:

```
foo at line 15
-----------
       6 | for i in range(5):
       7 |     row = [
       8 |         1,
       9 |         2,
       (...)
      12 |         5,
      13 |     ]
      14 |     result.append(row)
-->   15 |     print_stack()
      16 |     for j in range(5):
```

Alternatively, you can flip the condition around and check `if isinstance(line, stack_data.Line):`. Either way, you should always check for line gaps, or your code may appear to work at first but fail when it encounters a long piece.

Note that the executing piece, i.e. the piece containing the current line being executed (line 15 in this case) is never truncated, no matter how long it is.

The lines of context never stray outside `frame_info.scope`, which is the innermost function or class definition containing the current line. For example, this is the output for a short function which has neither 3 lines before nor 1 line after the current line:

```
bar at line 6
-----------
       4 | def bar():
       5 |     foo()
-->    6 |     print_stack()
```

Sometimes it's nice to ensure that the function signature is always showing. This can be done with `Options(include_signature=True)`. The result looks like this:

```
foo at line 14
-----------
       9 | def foo():
       (...)
      11 |     for i in range(5):
      12 |         row = []
      13 |         result.append(row)
```
