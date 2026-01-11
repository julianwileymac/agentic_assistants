# Chunk: 9dfdd9ba8d50_3

- source: `.venv-lab/Lib/site-packages/tornado/test/auth_test.py`
- lines: 227-299
- chunk: 4/9

```
     try:
            response = yield self.twitter_request(
                "/users/show/%s" % self.get_argument("name"),
                access_token=dict(key="hjkl", secret="vbnm"),
            )
        except HTTPClientError:
            # TODO(bdarnell): Should we catch HTTP errors and
            # transform some of them (like 403s) into AuthError?
            self.set_status(500)
            self.finish("error from twitter request")
        else:
            self.finish(response)


class TwitterServerAccessTokenHandler(RequestHandler):
    def get(self):
        self.write("oauth_token=hjkl&oauth_token_secret=vbnm&screen_name=foo")


class TwitterServerShowUserHandler(RequestHandler):
    def get(self, screen_name):
        if screen_name == "error":
            raise HTTPError(500)
        assert "oauth_nonce" in self.request.arguments
        assert "oauth_timestamp" in self.request.arguments
        assert "oauth_signature" in self.request.arguments
        assert self.get_argument("oauth_consumer_key") == "test_twitter_consumer_key"
        assert self.get_argument("oauth_signature_method") == "HMAC-SHA1"
        assert self.get_argument("oauth_version") == "1.0"
        assert self.get_argument("oauth_token") == "hjkl"
        self.write(dict(screen_name=screen_name, name=screen_name.capitalize()))


class TwitterServerVerifyCredentialsHandler(RequestHandler):
    def get(self):
        assert "oauth_nonce" in self.request.arguments
        assert "oauth_timestamp" in self.request.arguments
        assert "oauth_signature" in self.request.arguments
        assert self.get_argument("oauth_consumer_key") == "test_twitter_consumer_key"
        assert self.get_argument("oauth_signature_method") == "HMAC-SHA1"
        assert self.get_argument("oauth_version") == "1.0"
        assert self.get_argument("oauth_token") == "hjkl"
        self.write(dict(screen_name="foo", name="Foo"))


class AuthTest(AsyncHTTPTestCase):
    def get_app(self):
        return Application(
            [
                # test endpoints
                ("/openid/client/login", OpenIdClientLoginHandler, dict(test=self)),
                (
                    "/oauth10/client/login",
                    OAuth1ClientLoginHandler,
                    dict(test=self, version="1.0"),
                ),
                (
                    "/oauth10/client/request_params",
                    OAuth1ClientRequestParametersHandler,
                    dict(version="1.0"),
                ),
                (
                    "/oauth10a/client/login",
                    OAuth1ClientLoginHandler,
                    dict(test=self, version="1.0a"),
                ),
                (
                    "/oauth10a/client/login_coroutine",
                    OAuth1ClientLoginCoroutineHandler,
                    dict(test=self, version="1.0a"),
                ),
                (
```
