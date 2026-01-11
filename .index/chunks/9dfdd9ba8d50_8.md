# Chunk: 9dfdd9ba8d50_8

- source: `.venv-lab/Lib/site-packages/tornado/test/auth_test.py`
- lines: 541-609
- chunk: 9/9

```
ode)
            user = yield self.oauth2_request(
                self.test.get_url("/google/oauth2/userinfo"),
                access_token=access["access_token"],
            )
            # return the user and access token as json
            user["access_token"] = access["access_token"]
            self.write(user)
        else:
            self.authorize_redirect(
                redirect_uri=self._OAUTH_REDIRECT_URI,
                client_id=self.settings["google_oauth"]["key"],
                scope=["profile", "email"],
                response_type="code",
                extra_params={"prompt": "select_account"},
            )


class GoogleOAuth2AuthorizeHandler(RequestHandler):
    def get(self):
        # issue a fake auth code and redirect to redirect_uri
        code = "fake-authorization-code"
        self.redirect(url_concat(self.get_argument("redirect_uri"), dict(code=code)))


class GoogleOAuth2TokenHandler(RequestHandler):
    def post(self):
        assert self.get_argument("code") == "fake-authorization-code"
        # issue a fake token
        self.finish(
            {"access_token": "fake-access-token", "expires_in": "never-expires"}
        )


class GoogleOAuth2UserinfoHandler(RequestHandler):
    def get(self):
        assert self.get_argument("access_token") == "fake-access-token"
        # return a fake user
        self.finish({"name": "Foo", "email": "foo@example.com"})


class GoogleOAuth2Test(AsyncHTTPTestCase):
    def get_app(self):
        return Application(
            [
                # test endpoints
                ("/client/login", GoogleLoginHandler, dict(test=self)),
                # simulated google authorization server endpoints
                ("/google/oauth2/authorize", GoogleOAuth2AuthorizeHandler),
                ("/google/oauth2/token", GoogleOAuth2TokenHandler),
                ("/google/oauth2/userinfo", GoogleOAuth2UserinfoHandler),
            ],
            google_oauth={
                "key": "fake_google_client_id",
                "secret": "fake_google_client_secret",
            },
        )

    def test_google_login(self):
        response = self.fetch("/client/login")
        self.assertDictEqual(
            {
                "name": "Foo",
                "email": "foo@example.com",
                "access_token": "fake-access-token",
            },
            json_decode(response.body),
        )
```
