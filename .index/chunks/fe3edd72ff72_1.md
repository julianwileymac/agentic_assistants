# Chunk: fe3edd72ff72_1

- source: `.venv-lab/Lib/site-packages/nbconvert/exporters/webpdf.py`
- lines: 87-154
- chunk: 2/3

```
        cmd = [sys.executable, "-m", "playwright", "install", "chromium"]
                subprocess.check_call(cmd)  # noqa: S603

            playwright = await async_playwright().start()
            chromium = playwright.chromium

            try:
                browser = await chromium.launch(
                    handle_sigint=False, handle_sigterm=False, handle_sighup=False, args=args
                )
            except Exception as e:
                msg = (
                    "No suitable chromium executable found on the system. "
                    "Please use '--allow-chromium-download' to allow downloading one,"
                    "or install it using `playwright install chromium`."
                )
                await playwright.stop()
                raise RuntimeError(msg) from e

            page = await browser.new_page()
            await page.emulate_media(media="print")
            await page.wait_for_timeout(100)
            await page.goto(f"file://{temp_file.name}", wait_until="networkidle")
            await page.wait_for_timeout(100)

            pdf_params = {"print_background": True}
            if not self.paginate:
                # Floating point precision errors cause the printed
                # PDF from spilling over a new page by a pixel fraction.
                dimensions = await page.evaluate(
                    """() => {
                    const rect = document.body.getBoundingClientRect();
                    return {
                    width: Math.ceil(rect.width) + 1,
                    height: Math.ceil(rect.height) + 1,
                    }
                }"""
                )
                width = dimensions["width"]
                height = dimensions["height"]
                # 200 inches is the maximum size for Adobe Acrobat Reader.
                pdf_params.update(
                    {
                        "width": min(width, 200 * 72),
                        "height": min(height, 200 * 72),
                    }
                )
            pdf_data = await page.pdf(**pdf_params)

            await browser.close()
            await playwright.stop()
            return pdf_data

        pool = concurrent.futures.ThreadPoolExecutor()
        # Create a temporary file to pass the HTML code to Chromium:
        # Unfortunately, tempfile on Windows does not allow for an already open
        # file to be opened by a separate process. So we must close it first
        # before calling Chromium. We also specify delete=False to ensure the
        # file is not deleted after closing (the default behavior).
        temp_file = tempfile.NamedTemporaryFile(suffix=".html", delete=False)
        with temp_file:
            temp_file.write(html.encode("utf-8"))
        try:
            # TODO: when dropping Python 3.6, use
            # pdf_data = pool.submit(asyncio.run, main(temp_file)).result()
            def run_coroutine(coro):
                """Run an internal coroutine."""
```
