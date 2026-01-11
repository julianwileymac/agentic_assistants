# Chunk: 5acec92b1cb4_2

- source: `.venv-lab/Lib/site-packages/pygments/lexers/gdscript.py`
- lines: 126-190
- chunk: 3/3

```
kedFloat32Array", "PackedFloat64Array",
                    "PackedStringArray", "PackedVector2Array", "PackedVector3Array",
                    "PackedColorArray", "null", "void"),
                   prefix=r"(?<!\.)", suffix=r"\b"),
             Name.Builtin.Type),
        ],
        "numbers": [
            (r"(\d+\.\d*|\d*\.\d+)([eE][+-]?[0-9]+)?j?", Number.Float),
            (r"\d+[eE][+-]?[0-9]+j?", Number.Float),
            (r"0[xX][a-fA-F0-9]+", Number.Hex),
            (r"\d+j?", Number.Integer),
        ],
        "name": [(r"[a-zA-Z_]\w*", Name)],
        "funcname": [(r"[a-zA-Z_]\w*", Name.Function, "#pop"), default("#pop")],
        "classname": [(r"[a-zA-Z_]\w*", Name.Class, "#pop")],
        "stringescape": [
            (
                r'\\([\\abfnrtv"\']|\n|N\{.*?\}|u[a-fA-F0-9]{4}|'
                r"U[a-fA-F0-9]{8}|x[a-fA-F0-9]{2}|[0-7]{1,3})",
                String.Escape,
            )
        ],
        "strings-single": innerstring_rules(String.Single),
        "strings-double": innerstring_rules(String.Double),
        "dqs": [
            (r'"', String.Double, "#pop"),
            (r'\\\\|\\"|\\\n', String.Escape),  # included here for raw strings
            include("strings-double"),
        ],
        "sqs": [
            (r"'", String.Single, "#pop"),
            (r"\\\\|\\'|\\\n", String.Escape),  # included here for raw strings
            include("strings-single"),
        ],
        "tdqs": [
            (r'"""', String.Double, "#pop"),
            include("strings-double"),
            (r"\n", Whitespace),
        ],
        "tsqs": [
            (r"'''", String.Single, "#pop"),
            include("strings-single"),
            (r"\n", Whitespace),
        ],
    }

    def analyse_text(text):
        score = 0.0

        if re.search(
            r"func (_ready|_init|_input|_process|_unhandled_input)", text
        ):
            score += 0.8

        if re.search(
            r"(extends |class_name |onready |preload|load|setget|func [^_])",
            text
        ):
            score += 0.4

        if re.search(r"(var|const|enum|export|signal|tool)", text):
            score += 0.2

        return min(score, 1.0)
```
