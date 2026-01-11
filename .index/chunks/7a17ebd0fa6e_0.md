# Chunk: 7a17ebd0fa6e_0

- source: `.venv-lab/Lib/site-packages/debugpy/_vendored/pydevd/_pydev_bundle/_pydev_saved_modules.py`
- lines: 1-83
- chunk: 1/2

```
import sys
import os


def find_in_pythonpath(module_name):
    # Check all the occurrences where we could match the given module/package in the PYTHONPATH.
    #
    # This is a simplistic approach, but probably covers most of the cases we're interested in
    # (i.e.: this may fail in more elaborate cases of import customization or .zip imports, but
    # this should be rare in general).
    found_at = []

    parts = module_name.split(".")  # split because we need to convert mod.name to mod/name
    for path in sys.path:
        target = os.path.join(path, *parts)
        target_py = target + ".py"
        if os.path.isdir(target):
            found_at.append(target)
        if os.path.exists(target_py):
            found_at.append(target_py)
    return found_at


class DebuggerInitializationError(Exception):
    pass


class VerifyShadowedImport(object):
    def __init__(self, import_name):
        self.import_name = import_name

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            if exc_type == DebuggerInitializationError:
                return False  # It's already an error we generated.

            # We couldn't even import it...
            found_at = find_in_pythonpath(self.import_name)

            if len(found_at) <= 1:
                # It wasn't found anywhere or there was just 1 occurrence.
                # Let's just return to show the original error.
                return False

            # We found more than 1 occurrence of the same module in the PYTHONPATH
            # (the user module and the standard library module).
            # Let's notify the user as it seems that the module was shadowed.
            msg = self._generate_shadowed_import_message(found_at)
            raise DebuggerInitializationError(msg)

    def _generate_shadowed_import_message(self, found_at):
        msg = """It was not possible to initialize the debugger due to a module name conflict.

i.e.: the module "%(import_name)s" could not be imported because it is shadowed by:
%(found_at)s
Please rename this file/folder so that the original module from the standard library can be imported.""" % {
            "import_name": self.import_name,
            "found_at": found_at[0],
        }

        return msg

    def check(self, module, expected_attributes):
        msg = ""
        for expected_attribute in expected_attributes:
            try:
                getattr(module, expected_attribute)
            except:
                msg = self._generate_shadowed_import_message([module.__file__])
                break

        if msg:
            raise DebuggerInitializationError(msg)


with VerifyShadowedImport("threading") as verify_shadowed:
    import threading

    verify_shadowed.check(threading, ["Thread", "settrace", "setprofile", "Lock", "RLock", "current_thread"])
```
