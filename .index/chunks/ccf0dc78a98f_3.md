# Chunk: ccf0dc78a98f_3

- source: `.venv-lab/Lib/site-packages/setuptools/_vendor/tomli-2.0.1.dist-info/METADATA`
- lines: 186-207
- chunk: 4/4

```
ommands[0] | python -c 'import datetime; print(datetime.date.today())'
2021-07-23
benchmark-pypi run-test: commands[1] | python --version
Python 3.8.10
benchmark-pypi run-test: commands[2] | python benchmark/run.py
Parsing data.toml 5000 times:
------------------------------------------------------
    parser |  exec time | performance (more is better)
-----------+------------+-----------------------------
     rtoml |    0.901 s | baseline (100%)
  pytomlpp |     1.08 s | 83.15%
     tomli |     3.89 s | 23.15%
      toml |     9.36 s | 9.63%
     qtoml |     11.5 s | 7.82%
   tomlkit |     56.8 s | 1.59%
```

The parsers are ordered from fastest to slowest, using the fastest parser as baseline.
Tomli performed the best out of all pure Python TOML parsers,
losing only to pytomlpp (wraps C++) and rtoml (wraps Rust).
```
