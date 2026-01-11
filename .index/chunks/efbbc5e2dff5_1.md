# Chunk: efbbc5e2dff5_1

- source: `.venv-lab/Lib/site-packages/pygments/lexers/ldap.py`
- lines: 68-138
- chunk: 2/3

```
nctuation), ("#pop", "url")),
            (r'([-a-zA-Z0-9]*)(::?)',
             bygroups(Name.Property, Punctuation), ("#pop", "value")),
        ],
        'value': [
            (r'(\s*)([^\n]+\S)(\n )',
             bygroups(Whitespace, String, Whitespace)),
            (r'(\s*)([^\n]+\S)(\n)',
             bygroups(Whitespace, String, Whitespace), "#pop"),
        ],
        'url': [
            (r'([ \t]*)(\S*)([ \t]*\n )',
             bygroups(Whitespace, Comment.PreprocFile, Whitespace)),
            (r'([ \t]*)(\S*)([ \t]*\n)', bygroups(Whitespace,
             Comment.PreprocFile, Whitespace), "#pop"),
        ],
        "dn": [
            (r'([ \t]*)([-a-zA-Z0-9\.]+)(=)', bygroups(Whitespace,
             Name.Attribute, Operator), ("#pop", "dn-value")),
        ],
        "dn-value": [
            (r'\\[^\n]', Escape),
            (r',', Punctuation, ("#pop", "dn")),
            (r'\+', Operator, ("#pop", "dn")),
            (r'[^,\+\n]+', String),
            (r'\n ', Whitespace),
            (r'\n', Whitespace, "#pop"),
        ],
        "base64-dn": [
            (r'([ \t]*)([^ \t\n][^ \t\n]*[^\n])([ \t]*\n )',
             bygroups(Whitespace, Name, Whitespace)),
            (r'([ \t]*)([^ \t\n][^ \t\n]*[^\n])([ \t]*\n)',
             bygroups(Whitespace, Name, Whitespace), "#pop"),
        ]
    }


class LdaprcLexer(RegexLexer):
    """
    Lexer for OpenLDAP configuration files.
    """

    name = 'LDAP configuration file'
    aliases = ['ldapconf', 'ldaprc']
    filenames = ['.ldaprc', 'ldaprc', 'ldap.conf']
    mimetypes = ["text/x-ldapconf"]
    url = 'https://www.openldap.org/software//man.cgi?query=ldap.conf&sektion=5&apropos=0&manpath=OpenLDAP+2.4-Release'
    version_added = '2.17'

    _sasl_keywords = r'SASL_(?:MECH|REALM|AUTHCID|AUTHZID|CBINDING)'
    _tls_keywords = r'TLS_(?:CACERT|CACERTDIR|CERT|ECNAME|KEY|CIPHER_SUITE|PROTOCOL_MIN|RANDFILE|CRLFILE)'
    _literal_keywords = rf'(?:URI|SOCKET_BIND_ADDRESSES|{_sasl_keywords}|{_tls_keywords})'
    _boolean_keywords = r'GSSAPI_(?:ALLOW_REMOTE_PRINCIPAL|ENCRYPT|SIGN)|REFERRALS|SASL_NOCANON'
    _integer_keywords = r'KEEPALIVE_(?:IDLE|PROBES|INTERVAL)|NETWORK_TIMEOUT|PORT|SIZELIMIT|TIMELIMIT|TIMEOUT'
    _secprops = r'none|noanonymous|noplain|noactive|nodict|forwardsec|passcred|(?:minssf|maxssf|maxbufsize)=\d+'

    flags = re.IGNORECASE | re.MULTILINE

    tokens = {
        'root': [
            (r'#.*', Comment.Single),
            (r'\s+', Whitespace),
            (rf'({_boolean_keywords})(\s+)(on|true|yes|off|false|no)$',
             bygroups(Keyword, Whitespace, Keyword.Constant)),
            (rf'({_integer_keywords})(\s+)(\d+)',
             bygroups(Keyword, Whitespace, Number.Integer)),
            (r'(VERSION)(\s+)(2|3)', bygroups(Keyword, Whitespace, Number.Integer)),
            # Constants
            (r'(DEREF)(\s+)(never|searching|finding|always)',
             bygroups(Keyword, Whitespace, Keyword.Constant)),
```
