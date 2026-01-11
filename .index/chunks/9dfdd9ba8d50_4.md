# Chunk: 9dfdd9ba8d50_4

- source: `.venv-lab/Lib/site-packages/tornado/test/auth_test.py`
- lines: 290-354
- chunk: 5/9

```

                    dict(test=self, version="1.0a"),
                ),
                (
                    "/oauth10a/client/login_coroutine",
                    OAuth1ClientLoginCoroutineHandler,
                    dict(test=self, version="1.0a"),
                ),
                (
                    "/oauth10a/client/request_params",
                    OAuth1ClientRequestParametersHandler,
                    dict(version="1.0a"),
                ),
                ("/oauth2/client/login", OAuth2ClientLoginHandler, dict(test=self)),
                ("/facebook/client/login", FacebookClientLoginHandler, dict(test=self)),
                ("/twitter/client/login", TwitterClientLoginHandler, dict(test=self)),
                (
                    "/twitter/client/authenticate",
                    TwitterClientAuthenticateHandler,
                    dict(test=self),
                ),
                (
                    "/twitter/client/login_gen_coroutine",
                    TwitterClientLoginGenCoroutineHandler,
                    dict(test=self),
                ),
                (
                    "/twitter/client/show_user",
                    TwitterClientShowUserHandler,
                    dict(test=self),
                ),
                # simulated servers
                ("/openid/server/authenticate", OpenIdServerAuthenticateHandler),
                ("/oauth1/server/request_token", OAuth1ServerRequestTokenHandler),
                ("/oauth1/server/access_token", OAuth1ServerAccessTokenHandler),
                ("/facebook/server/access_token", FacebookServerAccessTokenHandler),
                ("/facebook/server/me", FacebookServerMeHandler),
                ("/twitter/server/access_token", TwitterServerAccessTokenHandler),
                (r"/twitter/api/users/show/(.*)\.json", TwitterServerShowUserHandler),
                (
                    r"/twitter/api/account/verify_credentials\.json",
                    TwitterServerVerifyCredentialsHandler,
                ),
            ],
            http_client=self.http_client,
            twitter_consumer_key="test_twitter_consumer_key",
            twitter_consumer_secret="test_twitter_consumer_secret",
            facebook_api_key="test_facebook_api_key",
            facebook_secret="test_facebook_secret",
        )

    def test_openid_redirect(self):
        response = self.fetch("/openid/client/login", follow_redirects=False)
        self.assertEqual(response.code, 302)
        self.assertIn("/openid/server/authenticate?", response.headers["Location"])

    def test_openid_get_user(self):
        response = self.fetch(
            "/openid/client/login?openid.mode=blah"
            "&openid.ns.ax=http://openid.net/srv/ax/1.0"
            "&openid.ax.type.email=http://axschema.org/contact/email"
            "&openid.ax.value.email=foo@example.com"
        )
        response.rethrow()
```
