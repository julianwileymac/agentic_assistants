# Chunk: bcc3c6bec4b8_18

- source: `.venv-lab/Lib/site-packages/pip/_vendor/distlib/util.py`
- lines: 1452-1521
- chunk: 19/25

```
_hostname, CertificateError)

    #
    # HTTPSConnection which verifies certificates/matches domains
    #

    class HTTPSConnection(httplib.HTTPSConnection):
        ca_certs = None  # set this to the path to the certs file (.pem)
        check_domain = True  # only used if ca_certs is not None

        # noinspection PyPropertyAccess
        def connect(self):
            sock = socket.create_connection((self.host, self.port), self.timeout)
            if getattr(self, '_tunnel_host', False):
                self.sock = sock
                self._tunnel()

            context = ssl.SSLContext(ssl.PROTOCOL_SSLv23)
            if hasattr(ssl, 'OP_NO_SSLv2'):
                context.options |= ssl.OP_NO_SSLv2
            if getattr(self, 'cert_file', None):
                context.load_cert_chain(self.cert_file, self.key_file)
            kwargs = {}
            if self.ca_certs:
                context.verify_mode = ssl.CERT_REQUIRED
                context.load_verify_locations(cafile=self.ca_certs)
                if getattr(ssl, 'HAS_SNI', False):
                    kwargs['server_hostname'] = self.host

            self.sock = context.wrap_socket(sock, **kwargs)
            if self.ca_certs and self.check_domain:
                try:
                    match_hostname(self.sock.getpeercert(), self.host)
                    logger.debug('Host verified: %s', self.host)
                except CertificateError:  # pragma: no cover
                    self.sock.shutdown(socket.SHUT_RDWR)
                    self.sock.close()
                    raise

    class HTTPSHandler(BaseHTTPSHandler):

        def __init__(self, ca_certs, check_domain=True):
            BaseHTTPSHandler.__init__(self)
            self.ca_certs = ca_certs
            self.check_domain = check_domain

        def _conn_maker(self, *args, **kwargs):
            """
            This is called to create a connection instance. Normally you'd
            pass a connection class to do_open, but it doesn't actually check for
            a class, and just expects a callable. As long as we behave just as a
            constructor would have, we should be OK. If it ever changes so that
            we *must* pass a class, we'll create an UnsafeHTTPSConnection class
            which just sets check_domain to False in the class definition, and
            choose which one to pass to do_open.
            """
            result = HTTPSConnection(*args, **kwargs)
            if self.ca_certs:
                result.ca_certs = self.ca_certs
                result.check_domain = self.check_domain
            return result

        def https_open(self, req):
            try:
                return self.do_open(self._conn_maker, req)
            except URLError as e:
                if 'certificate verify failed' in str(e.reason):
                    raise CertificateError('Unable to verify server certificate '
                                           'for %s' % req.host)
```
