# Chunk: daca156bbcb5_2

- source: `frontend/browser-app/lib/frontend/C_Users_Julian_Wiley_Documents_GitHub_agentic_assistants_frontend_node_modules_theia_core_lib-0053df.js`
- lines: 71-135
- chunk: 3/5

```
    const proxyUrl = this.preferenceService.get('http.proxy');
            const proxyAuthorization = this.preferenceService.get('http.proxyAuthorization');
            const strictSSL = this.preferenceService.get('http.proxyStrictSSL');
            return this.configure({
                proxyUrl,
                proxyAuthorization,
                strictSSL
            });
        });
        this.preferenceService.onPreferencesChanged(e => {
            this.configurePromise.then(() => {
                var _a, _b, _c;
                return this.configure({
                    proxyUrl: (_a = e['http.proxy']) === null || _a === void 0 ? void 0 : _a.newValue,
                    proxyAuthorization: (_b = e['http.proxyAuthorization']) === null || _b === void 0 ? void 0 : _b.newValue,
                    strictSSL: (_c = e['http.proxyStrictSSL']) === null || _c === void 0 ? void 0 : _c.newValue
                });
            });
        });
    }
};
(0, tslib_1.__decorate)([
    (0, inversify_1.inject)(preference_service_1.PreferenceService),
    (0, tslib_1.__metadata)("design:type", Object)
], AbstractBrowserRequestService.prototype, "preferenceService", void 0);
(0, tslib_1.__decorate)([
    (0, inversify_1.postConstruct)(),
    (0, tslib_1.__metadata)("design:type", Function),
    (0, tslib_1.__metadata)("design:paramtypes", []),
    (0, tslib_1.__metadata)("design:returntype", void 0)
], AbstractBrowserRequestService.prototype, "init", null);
AbstractBrowserRequestService = (0, tslib_1.__decorate)([
    (0, inversify_1.injectable)()
], AbstractBrowserRequestService);
exports.AbstractBrowserRequestService = AbstractBrowserRequestService;
let ProxyingBrowserRequestService = class ProxyingBrowserRequestService extends AbstractBrowserRequestService {
    configure(config) {
        return this.backendRequestService.configure(config);
    }
    resolveProxy(url) {
        return this.backendRequestService.resolveProxy(url);
    }
    async request(options) {
        // Wait for both the preferences and the configuration of the backend service
        await this.configurePromise;
        const backendResult = await this.backendRequestService.request(options);
        return request_1.RequestContext.decompress(backendResult);
    }
};
(0, tslib_1.__decorate)([
    (0, inversify_1.inject)(request_1.BackendRequestService),
    (0, tslib_1.__metadata)("design:type", Object)
], ProxyingBrowserRequestService.prototype, "backendRequestService", void 0);
ProxyingBrowserRequestService = (0, tslib_1.__decorate)([
    (0, inversify_1.injectable)()
], ProxyingBrowserRequestService);
exports.ProxyingBrowserRequestService = ProxyingBrowserRequestService;
let XHRBrowserRequestService = class XHRBrowserRequestService extends ProxyingBrowserRequestService {
    configure(config) {
        if (config.proxyAuthorization !== undefined) {
            this.authorization = config.proxyAuthorization;
        }
        return super.configure(config);
    }
```
