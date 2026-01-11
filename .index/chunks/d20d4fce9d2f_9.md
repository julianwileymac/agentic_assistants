# Chunk: d20d4fce9d2f_9

- source: `.venv-lab/Lib/site-packages/pip/_vendor/msgpack/fallback.py`
- lines: 711-776
- chunk: 10/12

```
       if 0xFFFF < obj <= 0xFFFFFFFF:
                    return self._buffer.write(struct.pack(">BI", 0xCE, obj))
                if -0x80000000 <= obj < -0x8000:
                    return self._buffer.write(struct.pack(">Bi", 0xD2, obj))
                if 0xFFFFFFFF < obj <= 0xFFFFFFFFFFFFFFFF:
                    return self._buffer.write(struct.pack(">BQ", 0xCF, obj))
                if -0x8000000000000000 <= obj < -0x80000000:
                    return self._buffer.write(struct.pack(">Bq", 0xD3, obj))
                if not default_used and self._default is not None:
                    obj = self._default(obj)
                    default_used = True
                    continue
                raise OverflowError("Integer value out of range")
            if check(obj, (bytes, bytearray)):
                n = len(obj)
                if n >= 2**32:
                    raise ValueError("%s is too large" % type(obj).__name__)
                self._pack_bin_header(n)
                return self._buffer.write(obj)
            if check(obj, str):
                obj = obj.encode("utf-8", self._unicode_errors)
                n = len(obj)
                if n >= 2**32:
                    raise ValueError("String is too large")
                self._pack_raw_header(n)
                return self._buffer.write(obj)
            if check(obj, memoryview):
                n = obj.nbytes
                if n >= 2**32:
                    raise ValueError("Memoryview is too large")
                self._pack_bin_header(n)
                return self._buffer.write(obj)
            if check(obj, float):
                if self._use_float:
                    return self._buffer.write(struct.pack(">Bf", 0xCA, obj))
                return self._buffer.write(struct.pack(">Bd", 0xCB, obj))
            if check(obj, (ExtType, Timestamp)):
                if check(obj, Timestamp):
                    code = -1
                    data = obj.to_bytes()
                else:
                    code = obj.code
                    data = obj.data
                assert isinstance(code, int)
                assert isinstance(data, bytes)
                L = len(data)
                if L == 1:
                    self._buffer.write(b"\xd4")
                elif L == 2:
                    self._buffer.write(b"\xd5")
                elif L == 4:
                    self._buffer.write(b"\xd6")
                elif L == 8:
                    self._buffer.write(b"\xd7")
                elif L == 16:
                    self._buffer.write(b"\xd8")
                elif L <= 0xFF:
                    self._buffer.write(struct.pack(">BB", 0xC7, L))
                elif L <= 0xFFFF:
                    self._buffer.write(struct.pack(">BH", 0xC8, L))
                else:
                    self._buffer.write(struct.pack(">BI", 0xC9, L))
                self._buffer.write(struct.pack("b", code))
                self._buffer.write(data)
                return
```
