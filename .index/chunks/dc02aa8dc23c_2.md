# Chunk: dc02aa8dc23c_2

- source: `.venv-lab/Lib/site-packages/ipywidgets/tests/test_embed.py`
- lines: 162-197
- chunk: 3/3

```
ads(data)
                    assert isinstance(view, dict)
                    self.states.append('check-widget-view')

        w = IntText(4)
        state = dependency_state(w, drop_defaults=True)
        snippet = embed_snippet(views=w, drop_defaults=True, state=state)
        parser = Parser()
        parser.feed(snippet)
        print(parser.states)
        assert parser.states == ['widget-state', 'check-widget-state', 'widget-view', 'check-widget-view']

    def test_minimal_html_filename(self):
        w = IntText(4)

        tmpd = tempfile.mkdtemp()

        try:
            output = os.path.join(tmpd, 'test.html')
            state = dependency_state(w, drop_defaults=True)
            embed_minimal_html(output, views=w, drop_defaults=True, state=state)
            # Check that the file is written to the intended destination:
            with open(output, 'r') as f:
                content = f.read()
            assert content.splitlines()[0] == '<!DOCTYPE html>'
        finally:
            shutil.rmtree(tmpd)

    def test_minimal_html_filehandle(self):
        w = IntText(4)
        output = StringIO()
        state = dependency_state(w, drop_defaults=True)
        embed_minimal_html(output, views=w, drop_defaults=True, state=state)
        content = output.getvalue()
        assert content.splitlines()[0] == '<!DOCTYPE html>'
```
