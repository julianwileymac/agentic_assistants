# Chunk: 5ff28b06adea_2

- source: `frontend/browser-app/lib/frontend/vendors-C_Users_Julian_Wiley_Documents_GitHub_agentic_assistants_frontend_node_modules_theia_-57c161.js`
- lines: 67-115
- chunk: 3/158

```
y\\Documents\\GitHub\\agentic_assistants\\frontend\\node_modules\\@theia\\core\\lib\\browser\\index.js");
const uri_1 = __webpack_require__(/*! @theia/core/lib/common/uri */ "C:\\Users\\Julian Wiley\\Documents\\GitHub\\agentic_assistants\\frontend\\node_modules\\@theia\\core\\lib\\common\\uri.js");
const preference_configurations_1 = __webpack_require__(/*! @theia/core/lib/browser/preferences/preference-configurations */ "C:\\Users\\Julian Wiley\\Documents\\GitHub\\agentic_assistants\\frontend\\node_modules\\@theia\\core\\lib\\browser\\preferences\\preference-configurations.js");
const promise_util_1 = __webpack_require__(/*! @theia/core/lib/common/promise-util */ "C:\\Users\\Julian Wiley\\Documents\\GitHub\\agentic_assistants\\frontend\\node_modules\\@theia\\core\\lib\\common\\promise-util.js");
const file_service_1 = __webpack_require__(/*! @theia/filesystem/lib/browser/file-service */ "C:\\Users\\Julian Wiley\\Documents\\GitHub\\agentic_assistants\\frontend\\node_modules\\@theia\\filesystem\\lib\\browser\\file-service.js");
const preference_transaction_manager_1 = __webpack_require__(/*! ./preference-transaction-manager */ "C:\\Users\\Julian Wiley\\Documents\\GitHub\\agentic_assistants\\frontend\\node_modules\\@theia\\preferences\\lib\\browser\\preference-transaction-manager.js");
const core_1 = __webpack_require__(/*! @theia/core */ "C:\\Users\\Julian Wiley\\Documents\\GitHub\\agentic_assistants\\frontend\\node_modules\\@theia\\core\\lib\\common\\index.js");
let AbstractResourcePreferenceProvider = class AbstractResourcePreferenceProvider extends browser_1.PreferenceProvider {
    constructor() {
        super(...arguments);
        this.preferences = {};
        this._fileExists = false;
        this.loading = new promise_util_1.Deferred();
        this.onDidChangeValidityEmitter = new core_1.Emitter();
    }
    set fileExists(exists) {
        if (exists !== this._fileExists) {
            this._fileExists = exists;
            this.onDidChangeValidityEmitter.fire(exists);
        }
    }
    get onDidChangeValidity() {
        return this.onDidChangeValidityEmitter.event;
    }
    init() {
        this.doInit();
    }
    async doInit() {
        const uri = this.getUri();
        this.toDispose.push(disposable_1.Disposable.create(() => this.loading.reject(new Error(`Preference provider for '${uri}' was disposed.`))));
        await this.readPreferencesFromFile();
        this._ready.resolve();
        this.loading.resolve();
        const storageUri = this.toFileManager().getConfigUri();
        this.toDispose.pushAll([
            this.fileService.watch(storageUri),
            this.fileService.onDidFilesChange(e => {
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
```
