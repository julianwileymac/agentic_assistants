# Chunk: db6cddaa5f29_7

- source: `.venv-lab/Lib/site-packages/debugpy/_vendored/pydevd/pydevconsole.py`
- lines: 533-612
- chunk: 8/8

```
es = traceback.format_list(tblist)
            if lines:
                lines.insert(0, "Traceback (most recent call last):\n")
            lines.extend(traceback.format_exception_only(type, value))
        finally:
            tblist = tb = None
        sys.stderr.write("".join(lines))


def console_exec(thread_id, frame_id, expression, dbg):
    """returns 'False' in case expression is partially correct"""
    frame = dbg.find_frame(thread_id, frame_id)

    is_multiline = expression.count("@LINE@") > 1
    expression = str(expression.replace("@LINE@", "\n"))

    # Not using frame.f_globals because of https://sourceforge.net/tracker2/?func=detail&aid=2541355&group_id=85796&atid=577329
    # (Names not resolved in generator expression in method)
    # See message: http://mail.python.org/pipermail/python-list/2009-January/526522.html
    updated_globals = {}
    updated_globals.update(frame.f_globals)
    updated_globals.update(frame.f_locals)  # locals later because it has precedence over the actual globals

    if IPYTHON:
        need_more = exec_code(CodeFragment(expression), updated_globals, frame.f_locals, dbg)
        if not need_more:
            pydevd_save_locals.save_locals(frame)
        return need_more

    interpreter = ConsoleWriter()

    if not is_multiline:
        try:
            code = compile_command(expression)
        except (OverflowError, SyntaxError, ValueError):
            # Case 1
            interpreter.showsyntaxerror()
            return False
        if code is None:
            # Case 2
            return True
    else:
        code = expression

    # Case 3

    try:
        Exec(code, updated_globals, frame.f_locals)

    except SystemExit:
        raise
    except:
        interpreter.showtraceback()
    else:
        pydevd_save_locals.save_locals(frame)
    return False


# =======================================================================================================================
# main
# =======================================================================================================================
if __name__ == "__main__":
    # Important: don't use this module directly as the __main__ module, rather, import itself as pydevconsole
    # so that we don't get multiple pydevconsole modules if it's executed directly (otherwise we'd have multiple
    # representations of its classes).
    # See: https://sw-brainwy.rhcloud.com/tracker/PyDev/446:
    # 'Variables' and 'Expressions' views stopped working when debugging interactive console
    import pydevconsole

    sys.stdin = pydevconsole.BaseStdIn(sys.stdin)
    port, client_port = sys.argv[1:3]
    from _pydev_bundle import pydev_localhost

    if int(port) == 0 and int(client_port) == 0:
        (h, p) = pydev_localhost.get_socket_name()

        client_port = p

    pydevconsole.start_server(pydev_localhost.get_localhost(), int(port), int(client_port))
```
