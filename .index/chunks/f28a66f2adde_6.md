# Chunk: f28a66f2adde_6

- source: `.venv-lab/Lib/site-packages/stack_data-0.6.3.dist-info/METADATA`
- lines: 351-444
- chunk: 7/7

```
ike this:

```
<module> at line 18
-----------
      14 |         for j in range(5):
      15 |             row.append(i * j)
      16 |     return result
-->   18 | bar()

bar at line 5
-----------
       4 | def bar():
-->    5 |     foo()

foo at line 13
-----------
      10 | for i in range(5):
      11 |     row = []
      12 |     result.append(row)
-->   13 |     print_stack()
      14 |     for j in range(5):
```

However, just as `frame_info.lines` doesn't always yield `Line` objects, `FrameInfo.stack_data` doesn't always yield `FrameInfo` objects, and we must modify our code to handle that. Let's look at some different sample code:

```python
def factorial(x):
    return x * factorial(x - 1)


try:
    print(factorial(5))
except:
    print_stack()
```

In this code we've forgotten to include a base case in our `factorial` function so it will fail with a `RecursionError` and there'll be many frames with similar information. Similar to the built in Python traceback, `stack_data` avoids showing all of these frames. Instead you will get a `RepeatedFrames` object which summarises the information. See its docstring for more details.

Here is our updated implementation:

```python
def print_stack():
    for frame_info in FrameInfo.stack_data(sys.exc_info()[2]):
        if isinstance(frame_info, FrameInfo):
            print(f"{frame_info.code.co_name} at line {frame_info.lineno}")
            print("-----------")
            for line in frame_info.lines:
                print(f"{'-->' if line.is_current else '   '} {line.lineno:4} | {line.render()}")

            for var in frame_info.variables:
                print(f"{var.name} = {repr(var.value)}")

            print()
        else:
            print(f"... {frame_info.description} ...\n")
```

And the output:

```
<module> at line 9
-----------
       4 | def factorial(x):
       5 |     return x * factorial(x - 1)
       8 | try:
-->    9 |     print(factorial(5))
      10 | except:

factorial at line 5
-----------
       4 | def factorial(x):
-->    5 |     return x * factorial(x - 1)
x = 5

factorial at line 5
-----------
       4 | def factorial(x):
-->    5 |     return x * factorial(x - 1)
x = 4

... factorial at line 5 (996 times) ...

factorial at line 5
-----------
       4 | def factorial(x):
-->    5 |     return x * factorial(x - 1)
x = -993
```

In addition to handling repeated frames, we've passed a traceback object to `FrameInfo.stack_data` instead of a frame.

If you want, you can pass `collapse_repeated_frames=False` to `FrameInfo.stack_data` (not to `Options`) and it will just yield `FrameInfo` objects for the full stack.
```
