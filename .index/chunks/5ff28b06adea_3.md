# Chunk: 5ff28b06adea_3

- source: `frontend/browser-app/lib/frontend/vendors-C_Users_Julian_Wiley_Documents_GitHub_agentic_assistants_frontend_node_modules_theia_-57c161.js`
- lines: 104-177
- chunk: 4/158

```
             if (e.contains(storageUri)) {
                    this.readPreferencesFromFile();
                }
            }),
            disposable_1.Disposable.create(() => this.reset()),
        ]);
    }
    get valid() {
        return this._fileExists;
    }
    getConfigUri(resourceUri) {
        if (!resourceUri) {
            return this.getUri();
        }
        return this.valid && this.contains(resourceUri) ? this.getUri() : undefined;
    }
    contains(resourceUri) {
        if (!resourceUri) {
            return true;
        }
        const domain = this.getDomain();
        if (!domain) {
            return true;
        }
        const resourcePath = new uri_1.default(resourceUri).path;
        return domain.some(uri => new uri_1.default(uri).path.relativity(resourcePath) >= 0);
    }
    getPreferences(resourceUri) {
        return this.valid && this.contains(resourceUri) ? this.preferences : {};
    }
    async setPreference(key, value, resourceUri) {
        let path;
        if (this.toDispose.disposed || !(path = this.getPath(key)) || !this.contains(resourceUri)) {
            return false;
        }
        return this.doSetPreference(key, path, value);
    }
    async doSetPreference(key, path, value) {
        var _a;
        if (!((_a = this.transaction) === null || _a === void 0 ? void 0 : _a.open)) {
            const current = this.transaction;
            this.transaction = this.transactionFactory(this.toFileManager(), current === null || current === void 0 ? void 0 : current.result);
            this.transaction.onWillConclude(({ status, waitUntil }) => {
                if (status) {
                    waitUntil((async () => {
                        await this.readPreferencesFromFile();
                        await this.fireDidPreferencesChanged(); // Ensure all consumers of the event have received it.
                    })());
                }
            });
            this.toDispose.push(this.transaction);
        }
        return this.transaction.enqueueAction(key, path, value);
    }
    /**
     * Use this method as intermediary for interactions with actual files.
     * Allows individual providers to modify where they store their files without disrupting the preference system's
     * conventions about scope and file location.
     */
    toFileManager() {
        return this;
    }
    getPath(preferenceName) {
        const asOverride = this.preferenceOverrideService.overriddenPreferenceName(preferenceName);
        if (asOverride === null || asOverride === void 0 ? void 0 : asOverride.overrideIdentifier) {
            return [this.preferenceOverrideService.markLanguageOverride(asOverride.overrideIdentifier), asOverride.preferenceName];
        }
        return [preferenceName];
    }
    async readPreferencesFromFile() {
        const content = await this.fileService.read(this.toFileManager().getConfigUri())
            .then(value => {
            this.fileExists = true;
```
