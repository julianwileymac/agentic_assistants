# Chunk: ed3d2fbb7d25_5

- source: `frontend/browser-app/lib/frontend/vendors-C_Users_Julian_Wiley_Documents_GitHub_agentic_assistants_frontend_node_modules_theia_-7f5c5b.js`
- lines: 206-267
- chunk: 6/6

```
ectURL(url);
            }
        }
    }
    request(uris) {
        const url = this.url(uris);
        const init = this.requestInit(uris);
        return new Request(url, init);
    }
    requestInit(uris) {
        if (uris.length === 1) {
            return {
                body: undefined,
                method: 'GET'
            };
        }
        return {
            method: 'PUT',
            body: JSON.stringify(this.body(uris)),
            headers: new Headers({ 'Content-Type': 'application/json' }),
        };
    }
    body(uris) {
        return {
            uris: uris.map(u => u.toString(true))
        };
    }
    url(uris) {
        const endpoint = this.endpoint();
        if (uris.length === 1) {
            // tslint:disable-next-line:whitespace
            const [uri,] = uris;
            return `${endpoint}/?uri=${uri.toString()}`;
        }
        return endpoint;
    }
    endpoint() {
        const url = this.filesUrl();
        return url.endsWith('/') ? url.slice(0, -1) : url;
    }
    filesUrl() {
        return new endpoint_1.Endpoint({ path: 'files' }).getRestUrl().toString();
    }
};
(0, tslib_1.__decorate)([
    (0, inversify_1.inject)(logger_1.ILogger),
    (0, tslib_1.__metadata)("design:type", Object)
], FileDownloadService.prototype, "logger", void 0);
(0, tslib_1.__decorate)([
    (0, inversify_1.inject)(message_service_1.MessageService),
    (0, tslib_1.__metadata)("design:type", message_service_1.MessageService)
], FileDownloadService.prototype, "messageService", void 0);
FileDownloadService = (0, tslib_1.__decorate)([
    (0, inversify_1.injectable)()
], FileDownloadService);
exports.FileDownloadService = FileDownloadService;


/***/ }

}]);
//# sourceMappingURL=vendors-C_Users_Julian_Wiley_Documents_GitHub_agentic_assistants_frontend_node_modules_theia_-7f5c5b.js.map
```
