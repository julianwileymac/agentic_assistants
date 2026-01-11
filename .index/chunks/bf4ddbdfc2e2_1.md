# Chunk: bf4ddbdfc2e2_1

- source: `.venv-lab/Lib/site-packages/debugpy/_vendored/pydevd/_pydevd_frame_eval/vendored/bytecode/tests/__init__.py`
- lines: 84-151
- chunk: 2/2

```
ode.kwonlyargcount)
            print(indent + "code.flags = %#x" % code.flags)
            if code.consts:
                print(indent + "code.consts = %r" % code.consts)
            if code.names:
                print(indent + "code.names = %r" % code.names)
            if code.varnames:
                print(indent + "code.varnames = %r" % code.varnames)

        for name in sorted(labels.values()):
            print(indent + "%s = Label()" % name)

        if is_concrete:
            text = indent + "code.extend("
            indent = " " * len(text)
        else:
            text = indent + "code = Bytecode("
            indent = " " * len(text)

        lines = _format_instr_list(code, labels, lineno).splitlines()
        last_line = len(lines) - 1
        for index, line in enumerate(lines):
            if index == 0:
                print(text + lines[0])
            elif index == last_line:
                print(indent + line + ")")
            else:
                print(indent + line)

        print()
    else:
        assert isinstance(code, ControlFlowGraph)
        labels = {}
        for block_index, block in enumerate(code):
            labels[id(block)] = "code[%s]" % block_index

        for block_index, block in enumerate(code):
            text = _format_instr_list(block, labels, lineno)
            if block_index != len(code) - 1:
                text += ","
            print(text)
            print()


def get_code(source, *, filename="<string>", function=False):
    source = textwrap.dedent(source).strip()
    code = compile(source, filename, "exec")
    if function:
        sub_code = [const for const in code.co_consts if isinstance(const, types.CodeType)]
        if len(sub_code) != 1:
            raise ValueError("unable to find function code")
        code = sub_code[0]
    return code


def disassemble(source, *, filename="<string>", function=False):
    code = get_code(source, filename=filename, function=function)
    return Bytecode.from_code(code)


class TestCase(unittest.TestCase):
    def assertBlocksEqual(self, code, *expected_blocks):
        self.assertEqual(len(code), len(expected_blocks))

        for block1, block2 in zip(code, expected_blocks):
            block_index = code.get_block_index(block1)
            self.assertListEqual(list(block1), block2, "Block #%s is different" % block_index)
```
