# Chunk: c9b8b1af4c6c_1

- source: `.venv-lab/Lib/site-packages/h11/_abnf.py`
- lines: 72-133
- chunk: 2/2

```
request.line
#
#   request-line   = method SP request-target SP HTTP-version CRLF
#   method         = token
#   HTTP-version   = HTTP-name "/" DIGIT "." DIGIT
#   HTTP-name      = %x48.54.54.50 ; "HTTP", case-sensitive
#
# request-target is complicated (see RFC 7230 sec 5.3) -- could be path, full
# URL, host+port (for connect), or even "*", but in any case we are guaranteed
# that it contists of the visible printing characters.
method = token
request_target = r"{vchar}+".format(**globals())
http_version = r"HTTP/(?P<http_version>[0-9]\.[0-9])"
request_line = (
    r"(?P<method>{method})"
    r" "
    r"(?P<target>{request_target})"
    r" "
    r"{http_version}".format(**globals())
)

# https://svn.tools.ietf.org/svn/wg/httpbis/specs/rfc7230.html#status.line
#
#   status-line = HTTP-version SP status-code SP reason-phrase CRLF
#   status-code    = 3DIGIT
#   reason-phrase  = *( HTAB / SP / VCHAR / obs-text )
status_code = r"[0-9]{3}"
reason_phrase = r"([ \t]|{vchar_or_obs_text})*".format(**globals())
status_line = (
    r"{http_version}"
    r" "
    r"(?P<status_code>{status_code})"
    # However, there are apparently a few too many servers out there that just
    # leave out the reason phrase:
    #   https://github.com/scrapy/scrapy/issues/345#issuecomment-281756036
    #   https://github.com/seanmonstar/httparse/issues/29
    # so make it optional. ?: is a non-capturing group.
    r"(?: (?P<reason>{reason_phrase}))?".format(**globals())
)

HEXDIG = r"[0-9A-Fa-f]"
# Actually
#
#      chunk-size     = 1*HEXDIG
#
# but we impose an upper-limit to avoid ridiculosity. len(str(2**64)) == 20
chunk_size = r"({HEXDIG}){{1,20}}".format(**globals())
# Actually
#
#     chunk-ext      = *( ";" chunk-ext-name [ "=" chunk-ext-val ] )
#
# but we aren't parsing the things so we don't really care.
chunk_ext = r";.*"
chunk_header = (
    r"(?P<chunk_size>{chunk_size})"
    r"(?P<chunk_ext>{chunk_ext})?"
    r"{OWS}\r\n".format(
        **globals()
    )  # Even though the specification does not allow for extra whitespaces,
    # we are lenient with trailing whitespaces because some servers on the wild use it.
)
```
