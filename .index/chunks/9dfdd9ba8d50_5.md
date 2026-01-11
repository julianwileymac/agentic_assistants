# Chunk: 9dfdd9ba8d50_5

- source: `.venv-lab/Lib/site-packages/tornado/test/auth_test.py`
- lines: 347-417
- chunk: 6/9

```
 response = self.fetch(
            "/openid/client/login?openid.mode=blah"
            "&openid.ns.ax=http://openid.net/srv/ax/1.0"
            "&openid.ax.type.email=http://axschema.org/contact/email"
            "&openid.ax.value.email=foo@example.com"
        )
        response.rethrow()
        parsed = json_decode(response.body)
        self.assertEqual(parsed["email"], "foo@example.com")

    def test_oauth10_redirect(self):
        response = self.fetch("/oauth10/client/login", follow_redirects=False)
        self.assertEqual(response.code, 302)
        self.assertTrue(
            response.headers["Location"].endswith(
                "/oauth1/server/authorize?oauth_token=zxcv"
            )
        )
        # the cookie is base64('zxcv')|base64('1234')
        self.assertIn(
            '_oauth_request_token="enhjdg==|MTIzNA=="',
            response.headers["Set-Cookie"],
            response.headers["Set-Cookie"],
        )

    def test_oauth10_get_user(self):
        response = self.fetch(
            "/oauth10/client/login?oauth_token=zxcv",
            headers={"Cookie": "_oauth_request_token=enhjdg==|MTIzNA=="},
        )
        response.rethrow()
        parsed = json_decode(response.body)
        self.assertEqual(parsed["email"], "foo@example.com")
        self.assertEqual(parsed["access_token"], dict(key="uiop", secret="5678"))

    def test_oauth10_request_parameters(self):
        response = self.fetch("/oauth10/client/request_params")
        response.rethrow()
        parsed = json_decode(response.body)
        self.assertEqual(parsed["oauth_consumer_key"], "asdf")
        self.assertEqual(parsed["oauth_token"], "uiop")
        self.assertIn("oauth_nonce", parsed)
        self.assertIn("oauth_signature", parsed)

    def test_oauth10a_redirect(self):
        response = self.fetch("/oauth10a/client/login", follow_redirects=False)
        self.assertEqual(response.code, 302)
        self.assertTrue(
            response.headers["Location"].endswith(
                "/oauth1/server/authorize?oauth_token=zxcv"
            )
        )
        # the cookie is base64('zxcv')|base64('1234')
        self.assertTrue(
            '_oauth_request_token="enhjdg==|MTIzNA=="'
            in response.headers["Set-Cookie"],
            response.headers["Set-Cookie"],
        )

    @unittest.skipIf(mock is None, "mock package not present")
    def test_oauth10a_redirect_error(self):
        with mock.patch.object(OAuth1ServerRequestTokenHandler, "get") as get:
            get.side_effect = Exception("boom")
            with ExpectLog(app_log, "Uncaught exception"):
                response = self.fetch("/oauth10a/client/login", follow_redirects=False)
            self.assertEqual(response.code, 500)

    def test_oauth10a_get_user(self):
        response = self.fetch(
            "/oauth10a/client/login?oauth_token=zxcv",
```
