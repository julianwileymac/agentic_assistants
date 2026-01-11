# Chunk: 5ff28b06adea_8

- source: `frontend/browser-app/lib/frontend/vendors-C_Users_Julian_Wiley_Documents_GitHub_agentic_assistants_frontend_node_modules_theia_-57c161.js`
- lines: 368-411
- chunk: 9/158

```
cuments\\GitHub\\agentic_assistants\\frontend\\node_modules\\@theia\\core\\shared\\inversify\\index.js");
const uri_1 = __webpack_require__(/*! @theia/core/lib/common/uri */ "C:\\Users\\Julian Wiley\\Documents\\GitHub\\agentic_assistants\\frontend\\node_modules\\@theia\\core\\lib\\common\\uri.js");
const preferences_1 = __webpack_require__(/*! @theia/core/lib/browser/preferences */ "C:\\Users\\Julian Wiley\\Documents\\GitHub\\agentic_assistants\\frontend\\node_modules\\@theia\\core\\lib\\browser\\preferences\\index.js");
const workspace_service_1 = __webpack_require__(/*! @theia/workspace/lib/browser/workspace-service */ "C:\\Users\\Julian Wiley\\Documents\\GitHub\\agentic_assistants\\frontend\\node_modules\\@theia\\workspace\\lib\\browser\\workspace-service.js");
const preference_configurations_1 = __webpack_require__(/*! @theia/core/lib/browser/preferences/preference-configurations */ "C:\\Users\\Julian Wiley\\Documents\\GitHub\\agentic_assistants\\frontend\\node_modules\\@theia\\core\\lib\\browser\\preferences\\preference-configurations.js");
const folder_preference_provider_1 = __webpack_require__(/*! ./folder-preference-provider */ "C:\\Users\\Julian Wiley\\Documents\\GitHub\\agentic_assistants\\frontend\\node_modules\\@theia\\preferences\\lib\\browser\\folder-preference-provider.js");
let FoldersPreferencesProvider = class FoldersPreferencesProvider extends preferences_1.PreferenceProvider {
    constructor() {
        super(...arguments);
        this.providers = new Map();
    }
    init() {
        this.doInit();
    }
    async doInit() {
        await this.workspaceService.roots;
        this.updateProviders();
        this.workspaceService.onWorkspaceChanged(() => this.updateProviders());
        const readyPromises = [];
        for (const provider of this.providers.values()) {
            readyPromises.push(provider.ready.catch(e => console.error(e)));
        }
        Promise.all(readyPromises).then(() => this._ready.resolve());
    }
    updateProviders() {
        const roots = this.workspaceService.tryGetRoots();
        const toDelete = new Set(this.providers.keys());
        for (const folder of roots) {
            for (const configPath of this.configurations.getPaths()) {
                for (const configName of [...this.configurations.getSectionNames(), this.configurations.getConfigName()]) {
                    const sectionUri = this.configurations.createUri(folder.resource, configPath, configName);
                    const sectionKey = sectionUri.toString();
                    toDelete.delete(sectionKey);
                    if (!this.providers.has(sectionKey)) {
                        const provider = this.createProvider(sectionUri, configName, folder);
                        this.providers.set(sectionKey, provider);
                    }
                }
            }
        }
        for (const key of toDelete) {
            const provider = this.providers.get(key);
            if (provider) {
```
