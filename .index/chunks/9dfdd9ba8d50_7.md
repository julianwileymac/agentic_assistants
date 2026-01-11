# Chunk: 9dfdd9ba8d50_7

- source: `.venv-lab/Lib/site-packages/tornado/test/auth_test.py`
- lines: 469-548
- chunk: 8/9

```
-Cookie"],
            response.headers["Set-Cookie"],
        )

    def test_twitter_redirect(self):
        self.base_twitter_redirect("/twitter/client/login")

    def test_twitter_redirect_gen_coroutine(self):
        self.base_twitter_redirect("/twitter/client/login_gen_coroutine")

    def test_twitter_authenticate_redirect(self):
        response = self.fetch("/twitter/client/authenticate", follow_redirects=False)
        self.assertEqual(response.code, 302)
        self.assertTrue(
            response.headers["Location"].endswith(
                "/twitter/server/authenticate?oauth_token=zxcv"
            ),
            response.headers["Location"],
        )
        # the cookie is base64('zxcv')|base64('1234')
        self.assertIn(
            '_oauth_request_token="enhjdg==|MTIzNA=="',
            response.headers["Set-Cookie"],
            response.headers["Set-Cookie"],
        )

    def test_twitter_get_user(self):
        response = self.fetch(
            "/twitter/client/login?oauth_token=zxcv",
            headers={"Cookie": "_oauth_request_token=enhjdg==|MTIzNA=="},
        )
        response.rethrow()
        parsed = json_decode(response.body)
        self.assertEqual(
            parsed,
            {
                "access_token": {
                    "key": "hjkl",
                    "screen_name": "foo",
                    "secret": "vbnm",
                },
                "name": "Foo",
                "screen_name": "foo",
                "username": "foo",
            },
        )

    def test_twitter_show_user(self):
        response = self.fetch("/twitter/client/show_user?name=somebody")
        response.rethrow()
        self.assertEqual(
            json_decode(response.body), {"name": "Somebody", "screen_name": "somebody"}
        )

    def test_twitter_show_user_error(self):
        response = self.fetch("/twitter/client/show_user?name=error")
        self.assertEqual(response.code, 500)
        self.assertEqual(response.body, b"error from twitter request")


class GoogleLoginHandler(RequestHandler, GoogleOAuth2Mixin):
    def initialize(self, test):
        self.test = test
        self._OAUTH_REDIRECT_URI = test.get_url("/client/login")
        self._OAUTH_AUTHORIZE_URL = test.get_url("/google/oauth2/authorize")
        self._OAUTH_ACCESS_TOKEN_URL = test.get_url("/google/oauth2/token")

    @gen.coroutine
    def get(self):
        code = self.get_argument("code", None)
        if code is not None:
            # retrieve authenticate google user
            access = yield self.get_authenticated_user(self._OAUTH_REDIRECT_URI, code)
            user = yield self.oauth2_request(
                self.test.get_url("/google/oauth2/userinfo"),
                access_token=access["access_token"],
            )
            # return the user and access token as json
            user["access_token"] = access["access_token"]
```
