# Chunk: ac01e9f9eb6f_5

- source: `.venv-lab/Lib/site-packages/debugpy/_vendored/pydevd/_pydev_bundle/pydev_console_utils.py`
- lines: 350-452
- chunk: 6/9

```
get_namespace())
                obj = getattr(res, text[last_dot + 1 :])
            except:
                pass
        return obj

    def getDescription(self, text):
        try:
            obj = self.__resolve_reference__(text)
            if obj is None:
                return ""
            return get_description(obj)
        except:
            return ""

    def do_exec_code(self, code, is_single_line):
        try:
            code_fragment = CodeFragment(code, is_single_line)
            more = self.need_more(code_fragment)
            if not more:
                code_fragment = self.buffer
                self.buffer = None
                self.exec_queue.put(code_fragment)

            return more
        except:
            traceback.print_exc()
            return False

    def execLine(self, line):
        return self.do_exec_code(line, True)

    def execMultipleLines(self, lines):
        if IS_JYTHON:
            more = False
            for line in lines.split("\n"):
                more = self.do_exec_code(line, True)
            return more
        else:
            return self.do_exec_code(lines, False)

    def interrupt(self):
        self.buffer = None  # Also clear the buffer when it's interrupted.
        try:
            if self.interruptable:
                # Fix for #PyDev-500: Console interrupt can't interrupt on sleep
                interrupt_main_thread(self.mainThread)

            self.finish_exec(False)
            return True
        except:
            traceback.print_exc()
            return False

    def close(self):
        sys.exit(0)

    def start_exec(self):
        self.interruptable = True

    def get_server(self):
        if getattr(self, "host", None) is not None:
            return xmlrpclib.Server("http://%s:%s" % (self.host, self.client_port))
        else:
            return None

    server = property(get_server)

    def ShowConsole(self):
        server = self.get_server()
        if server is not None:
            server.ShowConsole()

    def finish_exec(self, more):
        self.interruptable = False

        server = self.get_server()

        if server is not None:
            return server.NotifyFinished(more)
        else:
            return True

    def getFrame(self):
        xml = StringIO()
        hidden_ns = self.get_ipython_hidden_vars_dict()
        xml.write("<xml>")
        xml.write(pydevd_xml.frame_vars_to_xml(self.get_namespace(), hidden_ns))
        xml.write("</xml>")

        return xml.getvalue()

    @silence_warnings_decorator
    def getVariable(self, attributes):
        xml = StringIO()
        xml.write("<xml>")
        val_dict = pydevd_vars.resolve_compound_var_object_fields(self.get_namespace(), attributes)
        if val_dict is None:
            val_dict = {}

        for k, val in val_dict.items():
            val = val_dict[k]
```
