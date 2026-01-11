# Chunk: 02ef8a6cbd1e_1

- source: `frontend/browser-app/lib/frontend/vendors-C_Users_Julian_Wiley_Documents_GitHub_agentic_assistants_frontend_node_modules_theia_-600e14.js`
- lines: 32-88
- chunk: 2/7

```
__webpack_require__(/*! ../../common/i18n/localization-server */ "C:\\Users\\Julian Wiley\\Documents\\GitHub\\agentic_assistants\\frontend\\node_modules\\@theia\\core\\lib\\common\\i18n\\localization-server.js");
let I18nPreloadContribution = class I18nPreloadContribution {
    async initialize() {
        const defaultLocale = frontend_application_config_provider_1.FrontendApplicationConfigProvider.get().defaultLocale;
        if (defaultLocale && !nls_1.nls.locale) {
            Object.assign(nls_1.nls, {
                locale: defaultLocale
            });
        }
        if (nls_1.nls.locale && nls_1.nls.locale !== nls_1.nls.defaultLocale) {
            const localization = await this.localizationServer.loadLocalization(nls_1.nls.locale);
            if (localization.languagePack) {
                nls_1.nls.localization = localization;
            }
            else {
                // In case the localization that we've loaded doesn't localize Theia completely (languagePack is false)
                // We simply reset the locale to the default again
                Object.assign(nls_1.nls, {
                    locale: defaultLocale || undefined
                });
            }
        }
    }
};
(0, tslib_1.__decorate)([
    (0, inversify_1.inject)(localization_server_1.LocalizationServer),
    (0, tslib_1.__metadata)("design:type", Object)
], I18nPreloadContribution.prototype, "localizationServer", void 0);
I18nPreloadContribution = (0, tslib_1.__decorate)([
    (0, inversify_1.injectable)()
], I18nPreloadContribution);
exports.I18nPreloadContribution = I18nPreloadContribution;


/***/ },

/***/ "C:\\Users\\Julian Wiley\\Documents\\GitHub\\agentic_assistants\\frontend\\node_modules\\@theia\\core\\lib\\browser\\preload\\os-preload-contribution.js"
/*!**************************************************************************************************************************************************!*\
  !*** C:\Users\Julian Wiley\Documents\GitHub\agentic_assistants\frontend\node_modules\@theia\core\lib\browser\preload\os-preload-contribution.js ***!
  \**************************************************************************************************************************************************/
(__unused_webpack_module, exports, __webpack_require__) {


// *****************************************************************************
// Copyright (C) 2023 TypeFox and others.
//
// This program and the accompanying materials are made available under the
// terms of the Eclipse Public License v. 2.0 which is available at
// http://www.eclipse.org/legal/epl-2.0.
//
// This Source Code may also be made available under the following Secondary
// Licenses when the conditions for such availability set forth in the Eclipse
// Public License v. 2.0 are satisfied: GNU General Public License, version 2
// with the GNU Classpath Exception which is available at
// https://www.gnu.org/software/classpath/license.html.
//
```
