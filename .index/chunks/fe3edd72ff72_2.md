# Chunk: fe3edd72ff72_2

- source: `.venv-lab/Lib/site-packages/nbconvert/exporters/webpdf.py`
- lines: 146-182
- chunk: 3/3

```

        with temp_file:
            temp_file.write(html.encode("utf-8"))
        try:
            # TODO: when dropping Python 3.6, use
            # pdf_data = pool.submit(asyncio.run, main(temp_file)).result()
            def run_coroutine(coro):
                """Run an internal coroutine."""
                loop = (
                    asyncio.ProactorEventLoop()  # type:ignore[attr-defined]
                    if IS_WINDOWS
                    else asyncio.new_event_loop()
                )

                asyncio.set_event_loop(loop)
                return loop.run_until_complete(coro)

            pdf_data = pool.submit(run_coroutine, main(temp_file)).result()
        finally:
            # Ensure the file is deleted even if playwright raises an exception
            os.unlink(temp_file.name)
        return pdf_data

    def from_notebook_node(self, nb, resources=None, **kw):
        """Convert from a notebook node."""
        html, resources = super().from_notebook_node(nb, resources=resources, **kw)

        self.log.info("Building PDF")
        pdf_data = self.run_playwright(html)
        self.log.info("PDF successfully created")

        # convert output extension to pdf
        # the writer above required it to be html
        resources["output_extension"] = ".pdf"

        return pdf_data, resources
```
