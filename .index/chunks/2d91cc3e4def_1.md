# Chunk: 2d91cc3e4def_1

- source: `.venv-lab/Lib/site-packages/ipywidgets/widgets/tests/test_widget_selection.py`
- lines: 88-108
- chunk: 2/2

```
    assert select.value == 'dup'
        assert select.label == 'dup'
        assert observations == [3]
        select.index = 2
        assert select.index == 2
        assert select.value == 'dup'
        assert select.label == 'dup'
        assert observations == [3, 2]
        select.index = 0
        assert select.index == 0
        assert select.value == 'first'
        assert select.label == 'first'
        assert observations == [3, 2, 0]

        # picks the first matching value
        select.value = 'dup'
        assert select.index == 2
        assert select.value == 'dup'
        assert select.label == 'dup'
        assert observations == [3, 2, 0, 2]
```
