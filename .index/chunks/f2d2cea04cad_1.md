# Chunk: f2d2cea04cad_1

- source: `.venv-lab/Lib/site-packages/pycparser/plyparser.py`
- lines: 81-134
- chunk: 2/2

```
arams = params
        return rule_func
    return decorate


def template(cls):
    """ Class decorator to generate rules from parameterized rule templates.

    See `parameterized` for more information on parameterized rules.
    """
    issued_nodoc_warning = False
    for attr_name in dir(cls):
        if attr_name.startswith('p_'):
            method = getattr(cls, attr_name)
            if hasattr(method, '_params'):
                # Remove the template method
                delattr(cls, attr_name)
                # Create parameterized rules from this method; only run this if
                # the method has a docstring. This is to address an issue when
                # pycparser's users are installed in -OO mode which strips
                # docstrings away.
                # See: https://github.com/eliben/pycparser/pull/198/ and
                #      https://github.com/eliben/pycparser/issues/197
                # for discussion.
                if method.__doc__ is not None:
                    _create_param_rules(cls, method)
                elif not issued_nodoc_warning:
                    warnings.warn(
                        'parsing methods must have __doc__ for pycparser to work properly',
                        RuntimeWarning,
                        stacklevel=2)
                    issued_nodoc_warning = True
    return cls


def _create_param_rules(cls, func):
    """ Create ply.yacc rules based on a parameterized rule function

    Generates new methods (one per each pair of parameters) based on the
    template rule function `func`, and attaches them to `cls`. The rule
    function's parameters must be accessible via its `_params` attribute.
    """
    for xxx, yyy in func._params:
        # Use the template method's body for each new method
        def param_rule(self, p):
            func(self, p)

        # Substitute in the params for the grammar rule and function name
        param_rule.__doc__ = func.__doc__.replace('xxx', xxx).replace('yyy', yyy)
        param_rule.__name__ = func.__name__.replace('xxx', xxx)

        # Attach the new method to the class
        setattr(cls, param_rule.__name__, param_rule)
```
