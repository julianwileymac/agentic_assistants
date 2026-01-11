# Chunk: f28a66f2adde_5

- source: `.venv-lab/Lib/site-packages/stack_data-0.6.3.dist-info/METADATA`
- lines: 315-369
- chunk: 6/7

```
a-value="[]">row</span> = []
      14 |         <span data-value="[[0, 0, 0, 0, 0], [0, 1, 2, 3, 4], [0, 2, 4, 6, 8], [0, 3, 6, 9, 12], []]">result</span>.append(<span data-value="[]">row</span>)
-->   15 |         print_stack()
      17 |         for <span data-value="4">j</span> in range(5):
```

`line.variable_ranges` is a list of RangeInLines for each Variable that appears at least partially in this line. The data attribute of the range is a pair `(variable, node)` where node is the particular AST node from the list `variable.nodes` that corresponds to this range.

You can also use `line.token_ranges` (e.g. if you want to do your own syntax highlighting) or `line.executing_node_ranges` if you want to highlight the currently executing node identified by the [`executing`](https://github.com/alexmojaki/executing) library. Or if you want to make your own range from an AST node, use `line.range_from_node(node, data)`. See the docstrings for more info.

### Syntax highlighting with Pygments

If you'd like pretty colored text without the work, you can let [Pygments](https://pygments.org/) do it for you. Just follow these steps:

1. `pip install pygments` separately as it's not a dependency of `stack_data`.
2. Create a pygments formatter object such as `HtmlFormatter` or `Terminal256Formatter`.
3. Pass the formatter to `Options` in the argument `pygments_formatter`.
4. Use `line.render(pygmented=True)` to get your formatted text. In this case you can't pass any markers to `render`.

If you want, you can also highlight the executing node in the frame in combination with the pygments syntax highlighting. For this you will need:

1. A pygments style - either a style class or a string that names it. See the [documentation on styles](https://pygments.org/docs/styles/) and the [styles gallery](https://blog.yjl.im/2015/08/pygments-styles-gallery.html).
2. A modification to make to the style for the executing node, which is a string such as `"bold"` or `"bg:#ffff00"` (yellow background). See the [documentation on style rules](https://pygments.org/docs/styles/#style-rules).
3. Pass these two things to `stack_data.style_with_executing_node(style, modifier)` to get a new style class.
4. Pass the new style to your formatter when you create it.

Note that this doesn't work with `TerminalFormatter` which just uses the basic ANSI colors and doesn't use the style passed to it in general.

## Getting the full stack

Currently `print_stack()` doesn't actually print the stack, it just prints one frame. Instead of `frame_info = FrameInfo(frame, options)`, let's do this:

```python
for frame_info in FrameInfo.stack_data(frame, options):
```

Now the output looks something like this:

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
```
