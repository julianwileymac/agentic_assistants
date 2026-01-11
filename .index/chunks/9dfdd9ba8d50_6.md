# Chunk: 9dfdd9ba8d50_6

- source: `.venv-lab/Lib/site-packages/tornado/test/auth_test.py`
- lines: 410-479
- chunk: 7/9

```
pp_log, "Uncaught exception"):
                response = self.fetch("/oauth10a/client/login", follow_redirects=False)
            self.assertEqual(response.code, 500)

    def test_oauth10a_get_user(self):
        response = self.fetch(
            "/oauth10a/client/login?oauth_token=zxcv",
            headers={"Cookie": "_oauth_request_token=enhjdg==|MTIzNA=="},
        )
        response.rethrow()
        parsed = json_decode(response.body)
        self.assertEqual(parsed["email"], "foo@example.com")
        self.assertEqual(parsed["access_token"], dict(key="uiop", secret="5678"))

    def test_oauth10a_request_parameters(self):
        response = self.fetch("/oauth10a/client/request_params")
        response.rethrow()
        parsed = json_decode(response.body)
        self.assertEqual(parsed["oauth_consumer_key"], "asdf")
        self.assertEqual(parsed["oauth_token"], "uiop")
        self.assertIn("oauth_nonce", parsed)
        self.assertIn("oauth_signature", parsed)

    def test_oauth10a_get_user_coroutine_exception(self):
        response = self.fetch(
            "/oauth10a/client/login_coroutine?oauth_token=zxcv&fail_in_get_user=true",
            headers={"Cookie": "_oauth_request_token=enhjdg==|MTIzNA=="},
        )
        self.assertEqual(response.code, 503)

    def test_oauth2_redirect(self):
        response = self.fetch("/oauth2/client/login", follow_redirects=False)
        self.assertEqual(response.code, 302)
        self.assertIn("/oauth2/server/authorize?", response.headers["Location"])

    def test_facebook_login(self):
        response = self.fetch("/facebook/client/login", follow_redirects=False)
        self.assertEqual(response.code, 302)
        self.assertTrue("/facebook/server/authorize?" in response.headers["Location"])
        response = self.fetch(
            "/facebook/client/login?code=1234", follow_redirects=False
        )
        self.assertEqual(response.code, 200)
        user = json_decode(response.body)
        self.assertEqual(user["access_token"], "asdf")
        self.assertEqual(user["session_expires"], "3600")

    def base_twitter_redirect(self, url):
        # Same as test_oauth10a_redirect
        response = self.fetch(url, follow_redirects=False)
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

    def test_twitter_redirect(self):
        self.base_twitter_redirect("/twitter/client/login")

    def test_twitter_redirect_gen_coroutine(self):
        self.base_twitter_redirect("/twitter/client/login_gen_coroutine")

```
