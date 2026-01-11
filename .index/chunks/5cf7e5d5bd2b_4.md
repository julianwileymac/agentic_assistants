# Chunk: 5cf7e5d5bd2b_4

- source: `.venv-lab/Lib/site-packages/IPython/utils/ipstruct.py`
- lines: 356-380
- chunk: 5/5

```
,new: old + ' ' + new

        # default policy is to keep current keys when there's a conflict
        conflict_solve = dict.fromkeys(self, preserve)

        # the conflict_solve dictionary is given by the user 'inverted': we
        # need a name-function mapping, it comes as a function -> names
        # dict. Make a local copy (b/c we'll make changes), replace user
        # strings for the three builtin policies and invert it.
        if __conflict_solve:
            inv_conflict_solve_user = __conflict_solve.copy()
            for name, func in [('preserve',preserve), ('update',update),
                               ('add',add), ('add_flip',add_flip),
                               ('add_s',add_s)]:
                if name in inv_conflict_solve_user.keys():
                    inv_conflict_solve_user[func] = inv_conflict_solve_user[name]
                    del inv_conflict_solve_user[name]
            conflict_solve.update(self.__dict_invert(inv_conflict_solve_user))
        for key in data_dict:
            if key not in self:
                self[key] = data_dict[key]
            else:
                self[key] = conflict_solve[key](self[key],data_dict[key])
```
