# Chunk: 680ed0abbd5e_1

- source: `.venv-lab/Lib/site-packages/jupyterlab/tests/test_announcements.py`
- lines: 46-98
- chunk: 2/6

```
_failure(mock_client, labserverapp, jp_fetch):
    response = await jp_fetch("lab", "api", "news", method="GET")

    assert response.code == 200
    payload = json.loads(response.body)
    assert payload["news"] == []


@patch("tornado.httpclient.AsyncHTTPClient", new_callable=fake_client_factory)
async def test_CheckForUpdateHandler_get_pypi_success(mock_client, labserverapp, jp_fetch):
    mock_client.body = FAKE_JUPYTERLAB_PYPI_JSON

    response = await jp_fetch("lab", "api", "update", method="GET")

    message = "A newer version (1000.0.0) of JupyterLab is available."
    assert response.code == 200
    payload = json.loads(response.body)
    assert payload["notification"]["message"] == message
    assert payload["notification"]["link"] == [
        "Read more…",
        "https://github.com/jupyterlab/jupyterlab/releases/tag/v1000.0.0",
    ]
    assert payload["notification"]["options"] == {
        "data": {"id": hashlib.sha1(message.encode()).hexdigest(), "tags": ["update"]}  # noqa: S324
    }


@patch("tornado.httpclient.AsyncHTTPClient", new_callable=fake_client_factory)
async def test_CheckForUpdateHandler_get_failure(mock_client, labserverapp, jp_fetch):
    response = await jp_fetch("lab", "api", "update", method="GET")

    assert response.code == 200
    payload = json.loads(response.body)
    assert payload["notification"] is None


FAKE_NO_SUMMARY_ATOM_FEED = b"""<?xml version='1.0' encoding='UTF-8'?><feed xmlns="http://www.w3.org/2005/Atom" xml:lang="en"><id>https://jupyterlab.github.io/assets/feed.xml</id><title>JupyterLab News</title><updated>2023-05-02T19:01:33.669598+00:00</updated><author><name>John Doe</name><email>john@example.de</email></author><link href="https://jupyterlab.github.io/assets/feed.xml" rel="self" type="application/atom+xml"/><link href="https://jupyterlab.github.io/assets/" rel="alternate" type="text/html"/><generator uri="https://lkiesow.github.io/python-feedgen" version="0.9.0">python-feedgen</generator><logo>http://ex.com/logo.jpg</logo><subtitle>Subscribe to get news about JupyterLab.</subtitle><entry><id>https://jupyterlab.github.io/assets/posts/2022/11/02/demo</id><title>Thanks for using JupyterLab</title><updated>2022-11-02T14:00:00+00:00</updated><link href="https://jupyterlab.github.io/assets/posts/2022/11/02/demo.html" rel="alternate" type="text/html" title="Thanks for using JupyterLab"/><published>2022-11-02T14:00:00+00:00</published></entry></feed>"""


@patch("tornado.httpclient.AsyncHTTPClient", new_callable=fake_client_factory)
async def test_NewsHandler_get_missing_summary(mock_client, labserverapp, jp_fetch):
    mock_client.body = FAKE_NO_SUMMARY_ATOM_FEED

    response = await jp_fetch("lab", "api", "news", method="GET")

    assert response.code == 200
    payload = json.loads(response.body)
    assert payload["news"] == [
        {
            "createdAt": 1667397600000.0,
            "message": "Thanks for using JupyterLab",
            "modifiedAt": 1667397600000.0,
```
