# Chunk: 2eeab456aadd_10

- source: `.venv-lab/Lib/site-packages/notebook/static/4105.5144c29f0bbce103fec4.js.map`
- lines: 1-1
- chunk: 11/11

```
     for (var _i = 1; _i < arguments.length; _i++) {\n            args[_i - 1] = arguments[_i];\n        }\n        var handler = this.nodeHandlers.get(node.kind) || this.visitDefault;\n        return handler.call.apply(handler, __spreadArray([this, node], __read(args), false));\n    };\n    AbstractVisitor.prototype.visitDefault = function (node) {\n        var e_2, _a;\n        var args = [];\n        for (var _i = 1; _i < arguments.length; _i++) {\n            args[_i - 1] = arguments[_i];\n        }\n        if (node instanceof Node_js_1.AbstractNode) {\n            try {\n                for (var _b = __values(node.childNodes), _c = _b.next(); !_c.done; _c = _b.next()) {\n                    var child = _c.value;\n                    this.visitNode.apply(this, __spreadArray([child], __read(args), false));\n                }\n            }\n            catch (e_2_1) { e_2 = { error: e_2_1 }; }\n            finally {\n                try {\n                    if (_c && !_c.done && (_a = _b.return)) _a.call(_b);\n                }\n                finally { if (e_2) throw e_2.error; }\n            }\n        }\n    };\n    AbstractVisitor.prototype.setNodeHandler = function (kind, handler) {\n        this.nodeHandlers.set(kind, handler);\n    };\n    AbstractVisitor.prototype.removeNodeHandler = function (kind) {\n        this.nodeHandlers.delete(kind);\n    };\n    return AbstractVisitor;\n}());\nexports.AbstractVisitor = AbstractVisitor;\n//# sourceMappingURL=Visitor.js.map"],"names":[],"sourceRoot":""}
```
