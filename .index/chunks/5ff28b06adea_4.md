# Chunk: 5ff28b06adea_4

- source: `frontend/browser-app/lib/frontend/vendors-C_Users_Julian_Wiley_Documents_GitHub_agentic_assistants_frontend_node_modules_theia_-57c161.js`
- lines: 169-242
- chunk: 5/158

```
sOverride.overrideIdentifier), asOverride.preferenceName];
        }
        return [preferenceName];
    }
    async readPreferencesFromFile() {
        const content = await this.fileService.read(this.toFileManager().getConfigUri())
            .then(value => {
            this.fileExists = true;
            return value;
        })
            .catch(() => {
            this.fileExists = false;
            return { value: '' };
        });
        this.readPreferencesFromContent(content.value);
    }
    readPreferencesFromContent(content) {
        let preferencesInJson;
        try {
            preferencesInJson = this.parse(content);
        }
        catch {
            preferencesInJson = {};
        }
        const parsedPreferences = this.getParsedContent(preferencesInJson);
        this.handlePreferenceChanges(parsedPreferences);
    }
    parse(content) {
        content = content.trim();
        if (!content) {
            return undefined;
        }
        const strippedContent = jsoncparser.stripComments(content);
        return jsoncparser.parse(strippedContent);
    }
    handlePreferenceChanges(newPrefs) {
        const oldPrefs = Object.assign({}, this.preferences);
        this.preferences = newPrefs;
        const prefNames = new Set([...Object.keys(oldPrefs), ...Object.keys(newPrefs)]);
        const prefChanges = [];
        const uri = this.getUri();
        for (const prefName of prefNames.values()) {
            const oldValue = oldPrefs[prefName];
            const newValue = newPrefs[prefName];
            const schemaProperties = this.schemaProvider.getCombinedSchema().properties[prefName];
            if (schemaProperties) {
                const scope = schemaProperties.scope;
                // do not emit the change event if the change is made out of the defined preference scope
                if (!this.schemaProvider.isValidInScope(prefName, this.getScope())) {
                    console.warn(`Preference ${prefName} in ${uri} can only be defined in scopes: ${browser_1.PreferenceScope.getScopeNames(scope).join(', ')}.`);
                    continue;
                }
            }
            if (!browser_1.PreferenceProvider.deepEqual(newValue, oldValue)) {
                prefChanges.push({
                    preferenceName: prefName, newValue, oldValue, scope: this.getScope(), domain: this.getDomain()
                });
            }
        }
        if (prefChanges.length > 0) {
            this.emitPreferencesChangedEvent(prefChanges);
        }
    }
    reset() {
        const preferences = this.preferences;
        this.preferences = {};
        const changes = [];
        for (const prefName of Object.keys(preferences)) {
            const value = preferences[prefName];
            if (value !== undefined) {
                changes.push({
                    preferenceName: prefName, newValue: undefined, oldValue: value, scope: this.getScope(), domain: this.getDomain()
                });
```
