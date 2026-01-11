# Chunk: 9e73dd0b3dce_1

- source: `.venv-lab/Lib/site-packages/debugpy/_vendored/pydevd/_pydev_bundle/pydev_ipython_console.py`
- lines: 74-96
- chunk: 2/2

```


    def get_ipython_hidden_vars_dict(self):
        try:
            if hasattr(self.interpreter, "ipython") and hasattr(self.interpreter.ipython, "user_ns_hidden"):
                user_ns_hidden = self.interpreter.ipython.user_ns_hidden
                if isinstance(user_ns_hidden, dict):
                    # Since IPython 2 dict `user_ns_hidden` contains hidden variables and values
                    user_hidden_dict = user_ns_hidden.copy()
                else:
                    # In IPython 1.x `user_ns_hidden` used to be a set with names of hidden variables
                    user_hidden_dict = dict([(key, val) for key, val in self.interpreter.ipython.user_ns.items() if key in user_ns_hidden])

                # while `_`, `__` and `___` were not initialized, they are not presented in `user_ns_hidden`
                user_hidden_dict.setdefault("_", "")
                user_hidden_dict.setdefault("__", "")
                user_hidden_dict.setdefault("___", "")

                return user_hidden_dict
        except:
            # Getting IPython variables shouldn't break loading frame variables
            traceback.print_exc()
```
