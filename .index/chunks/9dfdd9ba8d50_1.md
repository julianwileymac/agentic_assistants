# Chunk: 9dfdd9ba8d50_1

- source: `.venv-lab/Lib/site-packages/tornado/test/auth_test.py`
- lines: 78-159
- chunk: 2/9

```
ken):
        if self.get_argument("fail_in_get_user", None):
            raise Exception("failing in get_user")
        if access_token != dict(key="uiop", secret="5678"):
            raise Exception("incorrect access token %r" % access_token)
        return dict(email="foo@example.com")


class OAuth1ClientLoginCoroutineHandler(OAuth1ClientLoginHandler):
    """Replaces OAuth1ClientLoginCoroutineHandler's get() with a coroutine."""

    @gen.coroutine
    def get(self):
        if self.get_argument("oauth_token", None):
            # Ensure that any exceptions are set on the returned Future,
            # not simply thrown into the surrounding StackContext.
            try:
                yield self.get_authenticated_user()
            except Exception as e:
                self.set_status(503)
                self.write("got exception: %s" % e)
        else:
            yield self.authorize_redirect()


class OAuth1ClientRequestParametersHandler(RequestHandler, OAuthMixin):
    def initialize(self, version):
        self._OAUTH_VERSION = version

    def _oauth_consumer_token(self):
        return dict(key="asdf", secret="qwer")

    def get(self):
        params = self._oauth_request_parameters(
            "http://www.example.com/api/asdf",
            dict(key="uiop", secret="5678"),
            parameters=dict(foo="bar"),
        )
        self.write(params)


class OAuth1ServerRequestTokenHandler(RequestHandler):
    def get(self):
        self.write("oauth_token=zxcv&oauth_token_secret=1234")


class OAuth1ServerAccessTokenHandler(RequestHandler):
    def get(self):
        self.write("oauth_token=uiop&oauth_token_secret=5678")


class OAuth2ClientLoginHandler(RequestHandler, OAuth2Mixin):
    def initialize(self, test):
        self._OAUTH_AUTHORIZE_URL = test.get_url("/oauth2/server/authorize")

    def get(self):
        res = self.authorize_redirect()  # type: ignore
        assert res is None


class FacebookClientLoginHandler(RequestHandler, FacebookGraphMixin):
    def initialize(self, test):
        self._OAUTH_AUTHORIZE_URL = test.get_url("/facebook/server/authorize")
        self._OAUTH_ACCESS_TOKEN_URL = test.get_url("/facebook/server/access_token")
        self._FACEBOOK_BASE_URL = test.get_url("/facebook/server")

    @gen.coroutine
    def get(self):
        if self.get_argument("code", None):
            user = yield self.get_authenticated_user(
                redirect_uri=self.request.full_url(),
                client_id=self.settings["facebook_api_key"],
                client_secret=self.settings["facebook_secret"],
                code=self.get_argument("code"),
            )
            self.write(user)
        else:
            self.authorize_redirect(
                redirect_uri=self.request.full_url(),
                client_id=self.settings["facebook_api_key"],
                extra_params={"scope": "read_stream,offline_access"},
```
