# Chunk: dc02aa8dc23c_0

- source: `.venv-lab/Lib/site-packages/ipywidgets/tests/test_embed.py`
- lines: 1-89
- chunk: 1/3

```

from io import StringIO
from html.parser import HTMLParser
import json
import os
import re
import tempfile
import shutil

import traitlets

from ..widgets import IntSlider, IntText, Text, Widget, jslink, HBox, widget_serialization, widget as widget_module
from ..embed import embed_data, embed_snippet, embed_minimal_html, dependency_state


class CaseWidget(Widget):
    """Widget to test dependency traversal"""

    a = traitlets.Instance(Widget, allow_none=True).tag(sync=True, **widget_serialization)
    b = traitlets.Instance(Widget, allow_none=True).tag(sync=True, **widget_serialization)

    _model_name = traitlets.Unicode('CaseWidgetModel').tag(sync=True)

    other = traitlets.Dict().tag(sync=True, **widget_serialization)




class TestEmbed:

    def teardown(self):
        for w in tuple(widget_module._instances.values()):
            w.close()

    def test_embed_data_simple(self):
        w = IntText(4)
        state = dependency_state(w, drop_defaults=True)
        data = embed_data(views=w, drop_defaults=True, state=state)

        state = data['manager_state']['state']
        views = data['view_specs']

        assert len(state) == 3
        assert len(views) == 1

        model_names = [s['model_name'] for s in state.values()]
        assert 'IntTextModel' in model_names

    def test_cors(self):
        w = IntText(4)
        code = embed_snippet(w)
         # 1 is from the require
        assert len(re.findall(' crossorigin', code)) > 1
        f = StringIO()
        embed_minimal_html(f, w)
        assert len(re.findall(' crossorigin', f.getvalue())) > 1

        code = embed_snippet(w, cors=False, requirejs=False)
        assert ' crossorigin' not in code
        f = StringIO()
        embed_minimal_html(f, w, cors=False, requirejs=False)
        assert ' crossorigin' not in f.getvalue()

        code = embed_snippet(w, cors=False, requirejs=True)
        assert len(re.findall(' crossorigin', code)) == 1 # 1 is from the require, which is ok
        f = StringIO()
        embed_minimal_html(f, w, cors=False, requirejs=True)
        assert len(re.findall(' crossorigin', f.getvalue())) == 1 # 1 is from the require, which is ok

    def test_escape(self):
        w = Text('<script A> <ScRipt> </Script> <!-- --> <b>hi</b>')
        code = embed_snippet(w)
        assert code.find(r'<script A>') == -1
        assert code.find(r'\u003cscript A> \u003cScRipt> \u003c/Script> \u003c!-- --> <b>hi</b>') >= 0

        f = StringIO()
        embed_minimal_html(f, w)
        content = f.getvalue()
        assert content.find(r'<script A>') == -1
        assert content.find(r'\u003cscript A> \u003cScRipt> \u003c/Script> \u003c!-- --> <b>hi</b>') >= 0

    def test_embed_data_two_widgets(self):
        w1 = IntText(4)
        w2 = IntSlider(min=0, max=100)
        jslink((w1, 'value'), (w2, 'value'))
        state = dependency_state([w1, w2], drop_defaults=True)
        data = embed_data(views=[w1, w2], drop_defaults=True, state=state)
```
