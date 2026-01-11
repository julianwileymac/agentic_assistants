# Chunk: ac01e9f9eb6f_6

- source: `.venv-lab/Lib/site-packages/debugpy/_vendored/pydevd/_pydev_bundle/pydev_console_utils.py`
- lines: 443-518
- chunk: 7/9

```
attributes):
        xml = StringIO()
        xml.write("<xml>")
        val_dict = pydevd_vars.resolve_compound_var_object_fields(self.get_namespace(), attributes)
        if val_dict is None:
            val_dict = {}

        for k, val in val_dict.items():
            val = val_dict[k]
            evaluate_full_value = pydevd_xml.should_evaluate_full_value(val)
            xml.write(pydevd_vars.var_to_xml(val, k, evaluate_full_value=evaluate_full_value))

        xml.write("</xml>")

        return xml.getvalue()

    def getArray(self, attr, roffset, coffset, rows, cols, format):
        name = attr.split("\t")[-1]
        array = pydevd_vars.eval_in_context(name, self.get_namespace(), self.get_namespace())
        return pydevd_vars.table_like_struct_to_xml(array, name, roffset, coffset, rows, cols, format)

    def evaluate(self, expression):
        xml = StringIO()
        xml.write("<xml>")
        result = pydevd_vars.eval_in_context(expression, self.get_namespace(), self.get_namespace())
        xml.write(pydevd_vars.var_to_xml(result, expression))
        xml.write("</xml>")
        return xml.getvalue()

    @silence_warnings_decorator
    def loadFullValue(self, seq, scope_attrs):
        """
        Evaluate full value for async Console variables in a separate thread and send results to IDE side
        :param seq: id of command
        :param scope_attrs: a sequence of variables with their attributes separated by NEXT_VALUE_SEPARATOR
        (i.e.: obj\tattr1\tattr2NEXT_VALUE_SEPARATORobj2\attr1\tattr2)
        :return:
        """
        frame_variables = self.get_namespace()
        var_objects = []
        vars = scope_attrs.split(NEXT_VALUE_SEPARATOR)
        for var_attrs in vars:
            if "\t" in var_attrs:
                name, attrs = var_attrs.split("\t", 1)

            else:
                name = var_attrs
                attrs = None
            if name in frame_variables:
                var_object = pydevd_vars.resolve_var_object(frame_variables[name], attrs)
                var_objects.append((var_object, name))
            else:
                var_object = pydevd_vars.eval_in_context(name, frame_variables, frame_variables)
                var_objects.append((var_object, name))

        from _pydevd_bundle.pydevd_comm import GetValueAsyncThreadConsole

        py_db = getattr(self, "debugger", None)

        if py_db is None:
            py_db = get_global_debugger()

        if py_db is None:
            from pydevd import PyDB

            py_db = PyDB()

        t = GetValueAsyncThreadConsole(py_db, self.get_server(), seq, var_objects)
        t.start()

    def changeVariable(self, attr, value):
        def do_change_variable():
            Exec("%s=%s" % (attr, value), self.get_namespace(), self.get_namespace())

        # Important: it has to be really enabled in the main thread, so, schedule
```
