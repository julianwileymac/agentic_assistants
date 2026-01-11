# Chunk: fbce96b0ee42_1

- source: `.venv-lab/Lib/site-packages/jedi/third_party/typeshed/third_party/2and3/jinja2/nodes.pyi`
- lines: 127-256
- chunk: 2/2

```
elf): ...

class List(Literal):
    fields: Any
    def as_const(self, eval_ctx: Optional[Any] = ...): ...

class Dict(Literal):
    fields: Any
    def as_const(self, eval_ctx: Optional[Any] = ...): ...

class Pair(Helper):
    fields: Any
    def as_const(self, eval_ctx: Optional[Any] = ...): ...

class Keyword(Helper):
    fields: Any
    def as_const(self, eval_ctx: Optional[Any] = ...): ...

class CondExpr(Expr):
    fields: Any
    def as_const(self, eval_ctx: Optional[Any] = ...): ...

class Filter(Expr):
    fields: Any
    def as_const(self, eval_ctx: Optional[Any] = ...): ...

class Test(Expr):
    fields: Any

class Call(Expr):
    fields: Any
    def as_const(self, eval_ctx: Optional[Any] = ...): ...

class Getitem(Expr):
    fields: Any
    def as_const(self, eval_ctx: Optional[Any] = ...): ...
    def can_assign(self): ...

class Getattr(Expr):
    fields: Any
    def as_const(self, eval_ctx: Optional[Any] = ...): ...
    def can_assign(self): ...

class Slice(Expr):
    fields: Any
    def as_const(self, eval_ctx: Optional[Any] = ...): ...

class Concat(Expr):
    fields: Any
    def as_const(self, eval_ctx: Optional[Any] = ...): ...

class Compare(Expr):
    fields: Any
    def as_const(self, eval_ctx: Optional[Any] = ...): ...

class Operand(Helper):
    fields: Any

class Mul(BinExpr):
    operator: str

class Div(BinExpr):
    operator: str

class FloorDiv(BinExpr):
    operator: str

class Add(BinExpr):
    operator: str

class Sub(BinExpr):
    operator: str

class Mod(BinExpr):
    operator: str

class Pow(BinExpr):
    operator: str

class And(BinExpr):
    operator: str
    def as_const(self, eval_ctx: Optional[Any] = ...): ...

class Or(BinExpr):
    operator: str
    def as_const(self, eval_ctx: Optional[Any] = ...): ...

class Not(UnaryExpr):
    operator: str

class Neg(UnaryExpr):
    operator: str

class Pos(UnaryExpr):
    operator: str

class EnvironmentAttribute(Expr):
    fields: Any

class ExtensionAttribute(Expr):
    fields: Any

class ImportedName(Expr):
    fields: Any

class InternalName(Expr):
    fields: Any
    def __init__(self) -> None: ...

class MarkSafe(Expr):
    fields: Any
    def as_const(self, eval_ctx: Optional[Any] = ...): ...

class MarkSafeIfAutoescape(Expr):
    fields: Any
    def as_const(self, eval_ctx: Optional[Any] = ...): ...

class ContextReference(Expr): ...
class Continue(Stmt): ...
class Break(Stmt): ...

class Scope(Stmt):
    fields: Any

class EvalContextModifier(Stmt):
    fields: Any

class ScopedEvalContextModifier(EvalContextModifier):
    fields: Any
```
