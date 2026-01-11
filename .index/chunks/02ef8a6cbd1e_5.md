# Chunk: 02ef8a6cbd1e_5

- source: `frontend/browser-app/lib/frontend/vendors-C_Users_Julian_Wiley_Documents_GitHub_agentic_assistants_frontend_node_modules_theia_-600e14.js`
- lines: 183-225
- chunk: 6/7

```
 available at
// https://www.gnu.org/software/classpath/license.html.
//
// SPDX-License-Identifier: EPL-2.0 OR GPL-2.0-only WITH Classpath-exception-2.0
// *****************************************************************************
Object.defineProperty(exports, "__esModule", ({ value: true }));
exports.ThemePreloadContribution = void 0;
const tslib_1 = __webpack_require__(/*! tslib */ "C:\\Users\\Julian Wiley\\Documents\\GitHub\\agentic_assistants\\frontend\\node_modules\\tslib\\tslib.es6.mjs");
const frontend_application_config_provider_1 = __webpack_require__(/*! ../frontend-application-config-provider */ "C:\\Users\\Julian Wiley\\Documents\\GitHub\\agentic_assistants\\frontend\\node_modules\\@theia\\core\\lib\\browser\\frontend-application-config-provider.js");
const inversify_1 = __webpack_require__(/*! inversify */ "C:\\Users\\Julian Wiley\\Documents\\GitHub\\agentic_assistants\\frontend\\node_modules\\inversify\\lib\\cjs\\index.js");
const application_props_1 = __webpack_require__(/*! @theia/application-package/lib/application-props */ "C:\\Users\\Julian Wiley\\Documents\\GitHub\\agentic_assistants\\frontend\\node_modules\\@theia\\application-package\\lib\\application-props.js");
let ThemePreloadContribution = class ThemePreloadContribution {
    initialize() {
        var _a;
        const dark = (_a = window.matchMedia) === null || _a === void 0 ? void 0 : _a.call(window, '(prefers-color-scheme: dark)').matches;
        const value = window.localStorage.getItem(frontend_application_config_provider_1.DEFAULT_BACKGROUND_COLOR_STORAGE_KEY) || application_props_1.DefaultTheme.defaultBackgroundColor(dark);
        document.documentElement.style.setProperty('--theia-editor-background', value);
    }
};
ThemePreloadContribution = (0, tslib_1.__decorate)([
    (0, inversify_1.injectable)()
], ThemePreloadContribution);
exports.ThemePreloadContribution = ThemePreloadContribution;


/***/ },

/***/ "C:\\Users\\Julian Wiley\\Documents\\GitHub\\agentic_assistants\\frontend\\node_modules\\@theia\\core\\lib\\common\\i18n\\localization-server.js"
/*!******************************************************************************************************************************************!*\
  !*** C:\Users\Julian Wiley\Documents\GitHub\agentic_assistants\frontend\node_modules\@theia\core\lib\common\i18n\localization-server.js ***!
  \******************************************************************************************************************************************/
(__unused_webpack_module, exports) {


// *****************************************************************************
// Copyright (C) 2023 TypeFox and others.
//
// This program and the accompanying materials are made available under the
// terms of the Eclipse Public License v. 2.0 which is available at
// http://www.eclipse.org/legal/epl-2.0.
//
// This Source Code may also be made available under the following Secondary
```
