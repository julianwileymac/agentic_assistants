# Chunk: 680ed0abbd5e_3

- source: `.venv-lab/Lib/site-packages/jupyterlab/tests/test_announcements.py`
- lines: 132-175
- chunk: 4/6

```
/jupyterlab.github.io/assets/posts/2022/11/02/demo.html",
            ],
            "options": {
                "data": {
                    "id": "https://jupyterlab.github.io/assets/posts/2022/11/02/demo",
                    "tags": ["news"],
                }
            },
        }
    ]


FAKE_NO_PUBLISHED_ATOM_FEED = b"""<?xml version='1.0' encoding='UTF-8'?><feed xmlns="http://www.w3.org/2005/Atom" xml:lang="en"><id>https://jupyterlab.github.io/assets/feed.xml</id><title>JupyterLab News</title><updated>2023-05-02T19:32:08.566055+00:00</updated><author><name>John Doe</name><email>john@example.de</email></author><link href="https://jupyterlab.github.io/assets/feed.xml" rel="self" type="application/atom+xml"/><link href="https://jupyterlab.github.io/assets/" rel="alternate" type="text/html"/><generator uri="https://lkiesow.github.io/python-feedgen" version="0.9.0">python-feedgen</generator><logo>http://ex.com/logo.jpg</logo><subtitle>Subscribe to get news about JupyterLab.</subtitle><entry><id>https://jupyterlab.github.io/assets/posts/2022/11/02/demo</id><title>Thanks for using JupyterLab</title><updated>2022-11-02T14:00:00+00:00</updated><link href="https://jupyterlab.github.io/assets/posts/2022/11/02/demo.html" rel="alternate" type="text/html" title="Thanks for using JupyterLab"/><summary>Big thanks to you, beloved JupyterLab user.</summary></entry></feed>"""


@patch("tornado.httpclient.AsyncHTTPClient", new_callable=fake_client_factory)
async def test_NewsHandler_no_published(mock_client, labserverapp, jp_fetch):
    mock_client.body = FAKE_NO_PUBLISHED_ATOM_FEED

    response = await jp_fetch("lab", "api", "news", method="GET")

    assert response.code == 200
    payload = json.loads(response.body)
    assert payload["news"] == [
        {
            "createdAt": 1667397600000.0,
            "message": "Thanks for using JupyterLab\nBig thanks to you, beloved JupyterLab user.",
            "modifiedAt": 1667397600000.0,
            "type": "info",
            "link": [
                "Open full post",
                "https://jupyterlab.github.io/assets/posts/2022/11/02/demo.html",
            ],
            "options": {
                "data": {
                    "id": "https://jupyterlab.github.io/assets/posts/2022/11/02/demo",
                    "tags": ["news"],
                }
            },
        }
    ]
```
