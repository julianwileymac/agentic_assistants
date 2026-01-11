# Chunk: faf8ce6b523f_3

- source: `.venv-lab/Lib/site-packages/IPython/core/profiledir.py`
- lines: 232-245
- chunk: 4/4

```
eDir.

        This will create the profile directory if it doesn't exist.

        Parameters
        ----------
        profile_dir : unicode or str
            The path of the profile directory.
        """
        profile_dir = expand_path(profile_dir)
        if not os.path.isdir(profile_dir):
            raise ProfileDirError('Profile directory not found: %s' % profile_dir)
        return cls(location=profile_dir, config=config)
```
