# Chunk: daca156bbcb5_3

- source: `frontend/browser-app/lib/frontend/C_Users_Julian_Wiley_Documents_GitHub_agentic_assistants_frontend_node_modules_theia_core_lib-0053df.js`
- lines: 127-204
- chunk: 4/5

```
e;
let XHRBrowserRequestService = class XHRBrowserRequestService extends ProxyingBrowserRequestService {
    configure(config) {
        if (config.proxyAuthorization !== undefined) {
            this.authorization = config.proxyAuthorization;
        }
        return super.configure(config);
    }
    async request(options, token) {
        var _a;
        try {
            const xhrResult = await this.xhrRequest(options, token);
            const statusCode = (_a = xhrResult.res.statusCode) !== null && _a !== void 0 ? _a : 200;
            if (statusCode >= 400) {
                // We might've been blocked by the firewall
                // Try it through the backend request service
                return super.request(options);
            }
            return xhrResult;
        }
        catch {
            return super.request(options);
        }
    }
    xhrRequest(options, token) {
        const authorization = this.authorization || options.proxyAuthorization;
        if (authorization) {
            options.headers = {
                ...(options.headers || {}),
                'Proxy-Authorization': authorization
            };
        }
        const xhr = new XMLHttpRequest();
        return new Promise((resolve, reject) => {
            xhr.open(options.type || 'GET', options.url || '', true, options.user, options.password);
            this.setRequestHeaders(xhr, options);
            xhr.responseType = 'arraybuffer';
            xhr.onerror = () => reject(new Error(xhr.statusText && ('XHR failed: ' + xhr.statusText) || 'XHR failed'));
            xhr.onload = () => {
                resolve({
                    url: options.url,
                    res: {
                        statusCode: xhr.status,
                        headers: this.getResponseHeaders(xhr)
                    },
                    buffer: new Uint8Array(xhr.response)
                });
            };
            xhr.ontimeout = e => reject(new Error(`XHR timeout: ${options.timeout}ms`));
            if (options.timeout) {
                xhr.timeout = options.timeout;
            }
            xhr.send(options.data);
            token === null || token === void 0 ? void 0 : token.onCancellationRequested(() => {
                xhr.abort();
                reject();
            });
        });
    }
    setRequestHeaders(xhr, options) {
        if (options.headers) {
            for (const k of Object.keys(options.headers)) {
                switch (k) {
                    case 'User-Agent':
                    case 'Accept-Encoding':
                    case 'Content-Length':
                        // unsafe headers
                        continue;
                }
                xhr.setRequestHeader(k, options.headers[k]);
            }
        }
    }
    getResponseHeaders(xhr) {
        const headers = {};
        for (const line of xhr.getAllResponseHeaders().split(/\r\n|\n|\r/g)) {
            if (line) {
```
