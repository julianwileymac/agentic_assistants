# Chunk: bf4ddbdfc2e2_0

- source: `.venv-lab/Lib/site-packages/debugpy/_vendored/pydevd/_pydevd_frame_eval/vendored/bytecode/tests/__init__.py`
- lines: 1-91
- chunk: 1/2

```
import sys
import textwrap
import types
import unittest

from _pydevd_frame_eval.vendored.bytecode import (
    UNSET,
    Label,
    Instr,
    ConcreteInstr,
    BasicBlock,  # noqa
    Bytecode,
    ControlFlowGraph,
    ConcreteBytecode,
)


def _format_instr_list(block, labels, lineno):
    instr_list = []
    for instr in block:
        if not isinstance(instr, Label):
            if isinstance(instr, ConcreteInstr):
                cls_name = "ConcreteInstr"
            else:
                cls_name = "Instr"
            arg = instr.arg
            if arg is not UNSET:
                if isinstance(arg, Label):
                    arg = labels[arg]
                elif isinstance(arg, BasicBlock):
                    arg = labels[id(arg)]
                else:
                    arg = repr(arg)
                if lineno:
                    text = "%s(%r, %s, lineno=%s)" % (
                        cls_name,
                        instr.name,
                        arg,
                        instr.lineno,
                    )
                else:
                    text = "%s(%r, %s)" % (cls_name, instr.name, arg)
            else:
                if lineno:
                    text = "%s(%r, lineno=%s)" % (cls_name, instr.name, instr.lineno)
                else:
                    text = "%s(%r)" % (cls_name, instr.name)
        else:
            text = labels[instr]
        instr_list.append(text)
    return "[%s]" % ",\n ".join(instr_list)


def dump_bytecode(code, lineno=False):
    """
    Use this function to write unit tests: copy/paste its output to
    write a self.assertBlocksEqual() check.
    """
    print()

    if isinstance(code, (Bytecode, ConcreteBytecode)):
        is_concrete = isinstance(code, ConcreteBytecode)
        if is_concrete:
            block = list(code)
        else:
            block = code

        indent = " " * 8
        labels = {}
        for index, instr in enumerate(block):
            if isinstance(instr, Label):
                name = "label_instr%s" % index
                labels[instr] = name

        if is_concrete:
            name = "ConcreteBytecode"
            print(indent + "code = %s()" % name)
            if code.argcount:
                print(indent + "code.argcount = %s" % code.argcount)
            if sys.version_info > (3, 8):
                if code.posonlyargcount:
                    print(indent + "code.posonlyargcount = %s" % code.posonlyargcount)
            if code.kwonlyargcount:
                print(indent + "code.kwargonlycount = %s" % code.kwonlyargcount)
            print(indent + "code.flags = %#x" % code.flags)
            if code.consts:
                print(indent + "code.consts = %r" % code.consts)
            if code.names:
                print(indent + "code.names = %r" % code.names)
            if code.varnames:
```
