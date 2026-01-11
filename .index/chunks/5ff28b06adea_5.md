# Chunk: 5ff28b06adea_5

- source: `frontend/browser-app/lib/frontend/vendors-C_Users_Julian_Wiley_Documents_GitHub_agentic_assistants_frontend_node_modules_theia_-57c161.js`
- lines: 236-294
- chunk: 6/158

```
Object.keys(preferences)) {
            const value = preferences[prefName];
            if (value !== undefined) {
                changes.push({
                    preferenceName: prefName, newValue: undefined, oldValue: value, scope: this.getScope(), domain: this.getDomain()
                });
            }
        }
        if (changes.length > 0) {
            this.emitPreferencesChangedEvent(changes);
        }
    }
};
(0, tslib_1.__decorate)([
    (0, inversify_1.inject)(preference_transaction_manager_1.PreferenceTransactionFactory),
    (0, tslib_1.__metadata)("design:type", Function)
], AbstractResourcePreferenceProvider.prototype, "transactionFactory", void 0);
(0, tslib_1.__decorate)([
    (0, inversify_1.inject)(browser_1.PreferenceSchemaProvider),
    (0, tslib_1.__metadata)("design:type", browser_1.PreferenceSchemaProvider)
], AbstractResourcePreferenceProvider.prototype, "schemaProvider", void 0);
(0, tslib_1.__decorate)([
    (0, inversify_1.inject)(file_service_1.FileService),
    (0, tslib_1.__metadata)("design:type", file_service_1.FileService)
], AbstractResourcePreferenceProvider.prototype, "fileService", void 0);
(0, tslib_1.__decorate)([
    (0, inversify_1.inject)(preference_configurations_1.PreferenceConfigurations),
    (0, tslib_1.__metadata)("design:type", preference_configurations_1.PreferenceConfigurations)
], AbstractResourcePreferenceProvider.prototype, "configurations", void 0);
(0, tslib_1.__decorate)([
    (0, inversify_1.postConstruct)(),
    (0, tslib_1.__metadata)("design:type", Function),
    (0, tslib_1.__metadata)("design:paramtypes", []),
    (0, tslib_1.__metadata)("design:returntype", void 0)
], AbstractResourcePreferenceProvider.prototype, "init", null);
AbstractResourcePreferenceProvider = (0, tslib_1.__decorate)([
    (0, inversify_1.injectable)()
], AbstractResourcePreferenceProvider);
exports.AbstractResourcePreferenceProvider = AbstractResourcePreferenceProvider;


/***/ },

/***/ "C:\\Users\\Julian Wiley\\Documents\\GitHub\\agentic_assistants\\frontend\\node_modules\\@theia\\preferences\\lib\\browser\\folder-preference-provider.js"
/*!****************************************************************************************************************************************************!*\
  !*** C:\Users\Julian Wiley\Documents\GitHub\agentic_assistants\frontend\node_modules\@theia\preferences\lib\browser\folder-preference-provider.js ***!
  \****************************************************************************************************************************************************/
(__unused_webpack_module, exports, __webpack_require__) {

"use strict";

// *****************************************************************************
// Copyright (C) 2019 Ericsson and others.
//
// This program and the accompanying materials are made available under the
// terms of the Eclipse Public License v. 2.0 which is available at
// http://www.eclipse.org/legal/epl-2.0.
//
```
