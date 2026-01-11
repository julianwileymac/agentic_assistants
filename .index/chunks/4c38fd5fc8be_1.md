# Chunk: 4c38fd5fc8be_1

- source: `.venv-lab/Lib/site-packages/jupyterlab/pytest_plugin.py`
- lines: 82-115
- chunk: 2/2

```

</html>
"""
    )

    return _make_lab_app


@pytest.fixture
def labapp(jp_serverapp, make_lab_app):
    app = make_lab_app()
    app._link_jupyter_server_extension(jp_serverapp)
    app.initialize()
    return app


@pytest.fixture
def fetch_long(http_server_client, jp_auth_header, jp_base_url):
    """fetch fixture that handles auth, base_url, and path"""

    def client_fetch(*parts, headers=None, params=None, **kwargs):
        # Handle URL strings
        path_url = url_escape(url_path_join(*parts), plus=False)
        path_url = url_path_join(jp_base_url, path_url)
        params_url = urllib.parse.urlencode(params or {})
        url = path_url + "?" + params_url
        # Add auth keys to header
        headers = headers or {}
        headers.update(jp_auth_header)
        # Make request.
        return http_server_client.fetch(url, headers=headers, request_timeout=250, **kwargs)

    return client_fetch
```
