# Chunk: edcdb0c75a7d_1

- source: `.venv-lab/Lib/site-packages/debugpy/_vendored/pydevd/_pydevd_bundle/pydevd_api.py`
- lines: 83-167
- chunk: 2/20

```
class and function definitions, as they have their
            # own objects.
            for _, lineno in dis.findlinestarts(code):
                if lineno is not None:
                    yield lineno

            # For nested class and function definitions, their respective code objects
            # are constants referenced by this object.
            for const in code.co_consts:
                if isinstance(const, types.CodeType) and const.co_filename == code.co_filename:
                    for lineno in _get_code_lines(const):
                        yield lineno

        return iterate()


class PyDevdAPI(object):
    class VariablePresentation(object):
        def __init__(self, special="group", function="group", class_="group", protected="inline"):
            self._presentation = {
                DAPGrouper.SCOPE_SPECIAL_VARS: special,
                DAPGrouper.SCOPE_FUNCTION_VARS: function,
                DAPGrouper.SCOPE_CLASS_VARS: class_,
                DAPGrouper.SCOPE_PROTECTED_VARS: protected,
            }

        def get_presentation(self, scope):
            return self._presentation[scope]

    def run(self, py_db):
        py_db.ready_to_run = True

    def notify_initialize(self, py_db):
        py_db.on_initialize()

    def notify_configuration_done(self, py_db):
        py_db.on_configuration_done()

    def notify_disconnect(self, py_db):
        py_db.on_disconnect()

    def set_protocol(self, py_db, seq, protocol):
        set_protocol(protocol.strip())
        if get_protocol() in (HTTP_JSON_PROTOCOL, JSON_PROTOCOL):
            cmd_factory_class = NetCommandFactoryJson
        else:
            cmd_factory_class = NetCommandFactory

        if not isinstance(py_db.cmd_factory, cmd_factory_class):
            py_db.cmd_factory = cmd_factory_class()

        return py_db.cmd_factory.make_protocol_set_message(seq)

    def set_ide_os_and_breakpoints_by(self, py_db, seq, ide_os, breakpoints_by):
        """
        :param ide_os: 'WINDOWS' or 'UNIX'
        :param breakpoints_by: 'ID' or 'LINE'
        """
        if breakpoints_by == "ID":
            py_db._set_breakpoints_with_id = True
        else:
            py_db._set_breakpoints_with_id = False

        self.set_ide_os(ide_os)

        return py_db.cmd_factory.make_version_message(seq)

    def set_ide_os(self, ide_os):
        """
        :param ide_os: 'WINDOWS' or 'UNIX'
        """
        pydevd_file_utils.set_ide_os(ide_os)

    def set_gui_event_loop(self, py_db, gui_event_loop):
        py_db._gui_event_loop = gui_event_loop

    def send_error_message(self, py_db, msg):
        cmd = py_db.cmd_factory.make_warning_message("pydevd: %s\n" % (msg,))
        py_db.writer.add_command(cmd)

    def set_show_return_values(self, py_db, show_return_values):
        if show_return_values:
            py_db.show_return_values = True
        else:
```
