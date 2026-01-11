# Chunk: bcc3c6bec4b8_7

- source: `.venv-lab/Lib/site-packages/pip/_vendor/distlib/util.py`
- lines: 550-621
- chunk: 8/25

```
           outstream.close()
        self.record_as_written(outfile)

    def write_binary_file(self, path, data):
        self.ensure_dir(os.path.dirname(path))
        if not self.dry_run:
            if os.path.exists(path):
                os.remove(path)
            with open(path, 'wb') as f:
                f.write(data)
        self.record_as_written(path)

    def write_text_file(self, path, data, encoding):
        self.write_binary_file(path, data.encode(encoding))

    def set_mode(self, bits, mask, files):
        if os.name == 'posix' or (os.name == 'java' and os._name == 'posix'):
            # Set the executable bits (owner, group, and world) on
            # all the files specified.
            for f in files:
                if self.dry_run:
                    logger.info("changing mode of %s", f)
                else:
                    mode = (os.stat(f).st_mode | bits) & mask
                    logger.info("changing mode of %s to %o", f, mode)
                    os.chmod(f, mode)

    set_executable_mode = lambda s, f: s.set_mode(0o555, 0o7777, f)

    def ensure_dir(self, path):
        path = os.path.abspath(path)
        if path not in self.ensured and not os.path.exists(path):
            self.ensured.add(path)
            d, f = os.path.split(path)
            self.ensure_dir(d)
            logger.info('Creating %s' % path)
            if not self.dry_run:
                os.mkdir(path)
            if self.record:
                self.dirs_created.add(path)

    def byte_compile(self, path, optimize=False, force=False, prefix=None, hashed_invalidation=False):
        dpath = cache_from_source(path, not optimize)
        logger.info('Byte-compiling %s to %s', path, dpath)
        if not self.dry_run:
            if force or self.newer(path, dpath):
                if not prefix:
                    diagpath = None
                else:
                    assert path.startswith(prefix)
                    diagpath = path[len(prefix):]
            compile_kwargs = {}
            if hashed_invalidation and hasattr(py_compile, 'PycInvalidationMode'):
                if not isinstance(hashed_invalidation, py_compile.PycInvalidationMode):
                    hashed_invalidation = py_compile.PycInvalidationMode.CHECKED_HASH
                compile_kwargs['invalidation_mode'] = hashed_invalidation
            py_compile.compile(path, dpath, diagpath, True, **compile_kwargs)  # raise error
        self.record_as_written(dpath)
        return dpath

    def ensure_removed(self, path):
        if os.path.exists(path):
            if os.path.isdir(path) and not os.path.islink(path):
                logger.debug('Removing directory tree at %s', path)
                if not self.dry_run:
                    shutil.rmtree(path)
                if self.record:
                    if path in self.dirs_created:
                        self.dirs_created.remove(path)
            else:
                if os.path.islink(path):
```
