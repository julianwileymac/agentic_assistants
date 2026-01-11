# Chunk: 5ff28b06adea_9

- source: `frontend/browser-app/lib/frontend/vendors-C_Users_Julian_Wiley_Documents_GitHub_agentic_assistants_frontend_node_modules_theia_-57c161.js`
- lines: 402-473
- chunk: 10/158

```
s.createProvider(sectionUri, configName, folder);
                        this.providers.set(sectionKey, provider);
                    }
                }
            }
        }
        for (const key of toDelete) {
            const provider = this.providers.get(key);
            if (provider) {
                this.providers.delete(key);
                provider.dispose();
            }
        }
    }
    getConfigUri(resourceUri, sectionName = this.configurations.getConfigName()) {
        for (const provider of this.getFolderProviders(resourceUri)) {
            const configUri = provider.getConfigUri(resourceUri);
            if (configUri && this.configurations.getName(configUri) === sectionName) {
                return configUri;
            }
        }
        return undefined;
    }
    getContainingConfigUri(resourceUri, sectionName = this.configurations.getConfigName()) {
        for (const provider of this.getFolderProviders(resourceUri)) {
            const configUri = provider.getConfigUri();
            if (provider.contains(resourceUri) && this.configurations.getName(configUri) === sectionName) {
                return configUri;
            }
        }
        return undefined;
    }
    getDomain() {
        return this.workspaceService.tryGetRoots().map(root => root.resource.toString());
    }
    resolve(preferenceName, resourceUri) {
        const result = {};
        const groups = this.groupProvidersByConfigName(resourceUri);
        for (const group of groups.values()) {
            for (const provider of group) {
                const { value, configUri } = provider.resolve(preferenceName, resourceUri);
                if (configUri && value !== undefined) {
                    result.configUri = configUri;
                    result.value = preferences_1.PreferenceProvider.merge(result.value, value);
                    break;
                }
            }
        }
        return result;
    }
    getPreferences(resourceUri) {
        let result = {};
        const groups = this.groupProvidersByConfigName(resourceUri);
        for (const group of groups.values()) {
            for (const provider of group) {
                if (provider.getConfigUri(resourceUri)) {
                    const preferences = provider.getPreferences();
                    result = preferences_1.PreferenceProvider.merge(result, preferences);
                    break;
                }
            }
        }
        return result;
    }
    async setPreference(preferenceName, value, resourceUri) {
        const firstPathFragment = preferenceName.split('.', 1)[0];
        const defaultConfigName = this.configurations.getConfigName();
        const configName = this.configurations.isSectionName(firstPathFragment) ? firstPathFragment : defaultConfigName;
        const providers = this.getFolderProviders(resourceUri);
        let configPath;
        const candidates = providers.filter(provider => {
```
