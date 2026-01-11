# Chunk: c5efe5bd33ef_10

- source: `.venv-lab/Lib/site-packages/jupyter_server/base/handlers.py`
- lines: 701-784
- chunk: 11/17

```
y.strip().decode("utf-8")
        try:
            model = json.loads(body)
        except Exception as e:
            self.log.debug("Bad JSON: %r", body)
            self.log.error("Couldn't parse JSON", exc_info=True)
            raise web.HTTPError(400, "Invalid JSON in body of request") from e
        return cast("dict[str, Any]", model)

    def write_error(self, status_code: int, **kwargs: Any) -> None:
        """render custom error pages"""
        exc_info = kwargs.get("exc_info")
        message = ""
        status_message = responses.get(status_code, "Unknown HTTP Error")

        if exc_info:
            exception = exc_info[1]
            # get the custom message, if defined
            try:
                message = exception.log_message % exception.args
            except Exception:
                pass

            # construct the custom reason, if defined
            reason = getattr(exception, "reason", "")
            if reason:
                status_message = reason
        else:
            exception = "(unknown)"

        # build template namespace
        ns = {
            "status_code": status_code,
            "status_message": status_message,
            "message": message,
            "exception": exception,
        }

        self.set_header("Content-Type", "text/html")
        # render the template
        try:
            html = self.render_template("%s.html" % status_code, **ns)
        except TemplateNotFound:
            html = self.render_template("error.html", **ns)

        self.write(html)


class APIHandler(JupyterHandler):
    """Base class for API handlers"""

    async def prepare(self) -> None:  # type:ignore[override]
        """Prepare an API response."""
        await super().prepare()
        if not self.check_origin():
            raise web.HTTPError(404)

    def write_error(self, status_code: int, **kwargs: Any) -> None:
        """APIHandler errors are JSON, not human pages"""
        self.set_header("Content-Type", "application/json")
        message = responses.get(status_code, "Unknown HTTP Error")
        reply: dict[str, Any] = {
            "message": message,
        }
        exc_info = kwargs.get("exc_info")
        if exc_info:
            e = exc_info[1]
            if isinstance(e, HTTPError):
                reply["message"] = e.log_message or message
                reply["reason"] = e.reason
            else:
                reply["message"] = "Unhandled error"
                reply["reason"] = None
                # backward-compatibility: traceback field is present,
                # but always empty
                reply["traceback"] = ""
        self.log.warning("wrote error: %r", reply["message"], exc_info=True)
        self.finish(json.dumps(reply))

    def get_login_url(self) -> str:
        """Get the login url."""
        # if get_login_url is invoked in an API handler,
        # that means @web.authenticated is trying to trigger a redirect.
```
