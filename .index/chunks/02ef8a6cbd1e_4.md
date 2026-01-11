# Chunk: 02ef8a6cbd1e_4

- source: `frontend/browser-app/lib/frontend/vendors-C_Users_Julian_Wiley_Documents_GitHub_agentic_assistants_frontend_node_modules_theia_-600e14.js`
- lines: 149-189
- chunk: 5/7

```
 os_1 = __webpack_require__(/*! ../../common/os */ "C:\\Users\\Julian Wiley\\Documents\\GitHub\\agentic_assistants\\frontend\\node_modules\\@theia\\core\\lib\\common\\os.js");
exports["default"] = new inversify_1.ContainerModule(bind => {
    bind(preloader_1.Preloader).toSelf().inSingletonScope();
    (0, contribution_provider_1.bindContributionProvider)(bind, preloader_1.PreloadContribution);
    bind(localization_server_1.LocalizationServer).toDynamicValue(ctx => ws_connection_provider_1.WebSocketConnectionProvider.createProxy(ctx.container, localization_server_1.LocalizationServerPath)).inSingletonScope();
    bind(os_1.OSBackendProvider).toDynamicValue(ctx => ws_connection_provider_1.WebSocketConnectionProvider.createProxy(ctx.container, os_1.OSBackendProviderPath)).inSingletonScope();
    bind(i18n_preload_contribution_1.I18nPreloadContribution).toSelf().inSingletonScope();
    bind(preloader_1.PreloadContribution).toService(i18n_preload_contribution_1.I18nPreloadContribution);
    bind(os_preload_contribution_1.OSPreloadContribution).toSelf().inSingletonScope();
    bind(preloader_1.PreloadContribution).toService(os_preload_contribution_1.OSPreloadContribution);
    bind(theme_preload_contribution_1.ThemePreloadContribution).toSelf().inSingletonScope();
    bind(preloader_1.PreloadContribution).toService(theme_preload_contribution_1.ThemePreloadContribution);
});


/***/ },

/***/ "C:\\Users\\Julian Wiley\\Documents\\GitHub\\agentic_assistants\\frontend\\node_modules\\@theia\\core\\lib\\browser\\preload\\theme-preload-contribution.js"
/*!*****************************************************************************************************************************************************!*\
  !*** C:\Users\Julian Wiley\Documents\GitHub\agentic_assistants\frontend\node_modules\@theia\core\lib\browser\preload\theme-preload-contribution.js ***!
  \*****************************************************************************************************************************************************/
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
// SPDX-License-Identifier: EPL-2.0 OR GPL-2.0-only WITH Classpath-exception-2.0
// *****************************************************************************
Object.defineProperty(exports, "__esModule", ({ value: true }));
```
