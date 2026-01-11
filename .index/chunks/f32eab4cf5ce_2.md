# Chunk: f32eab4cf5ce_2

- source: `.venv-lab/Lib/site-packages/pip/_vendor/cachecontrol/adapter.py`
- lines: 138-169
- chunk: 3/3

```
update_chunk_length(
                        weak_self: weakref.ReferenceType[HTTPResponse],
                    ) -> None:
                        self = weak_self()
                        if self is None:
                            return

                        super_update_chunk_length(self)
                        if self.chunk_left == 0:
                            self._fp._close()  # type: ignore[union-attr]

                    response._update_chunk_length = functools.partial(  # type: ignore[method-assign]
                        _update_chunk_length, weakref.ref(response)
                    )

        resp: Response = super().build_response(request, response)

        # See if we should invalidate the cache.
        if request.method in self.invalidating_methods and resp.ok:
            assert request.url is not None
            cache_url = self.controller.cache_url(request.url)
            self.cache.delete(cache_url)

        # Give the request a from_cache attr to let people use it
        resp.from_cache = from_cache  # type: ignore[attr-defined]

        return resp

    def close(self) -> None:
        self.cache.close()
        super().close()  # type: ignore[no-untyped-call]
```
