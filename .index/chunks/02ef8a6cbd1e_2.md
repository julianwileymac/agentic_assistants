# Chunk: 02ef8a6cbd1e_2

- source: `frontend/browser-app/lib/frontend/vendors-C_Users_Julian_Wiley_Documents_GitHub_agentic_assistants_frontend_node_modules_theia_-600e14.js`
- lines: 82-133
- chunk: 3/7

```
r the following Secondary
// Licenses when the conditions for such availability set forth in the Eclipse
// Public License v. 2.0 are satisfied: GNU General Public License, version 2
// with the GNU Classpath Exception which is available at
// https://www.gnu.org/software/classpath/license.html.
//
// SPDX-License-Identifier: EPL-2.0 OR GPL-2.0-only WITH Classpath-exception-2.0
// *****************************************************************************
Object.defineProperty(exports, "__esModule", ({ value: true }));
exports.OSPreloadContribution = void 0;
const tslib_1 = __webpack_require__(/*! tslib */ "C:\\Users\\Julian Wiley\\Documents\\GitHub\\agentic_assistants\\frontend\\node_modules\\tslib\\tslib.es6.mjs");
const inversify_1 = __webpack_require__(/*! inversify */ "C:\\Users\\Julian Wiley\\Documents\\GitHub\\agentic_assistants\\frontend\\node_modules\\inversify\\lib\\cjs\\index.js");
const common_1 = __webpack_require__(/*! ../../common */ "C:\\Users\\Julian Wiley\\Documents\\GitHub\\agentic_assistants\\frontend\\node_modules\\@theia\\core\\lib\\common\\index.js");
let OSPreloadContribution = class OSPreloadContribution {
    async initialize() {
        const osType = await this.osBackendProvider.getBackendOS();
        const isWindows = osType === 'Windows';
        const isOSX = osType === 'OSX';
        common_1.OS.backend.isOSX = isOSX;
        common_1.OS.backend.isWindows = isWindows;
        common_1.OS.backend.type = () => osType;
        common_1.OS.backend.EOL = isWindows ? '\r\n' : '\n';
    }
};
(0, tslib_1.__decorate)([
    (0, inversify_1.inject)(common_1.OSBackendProvider),
    (0, tslib_1.__metadata)("design:type", Object)
], OSPreloadContribution.prototype, "osBackendProvider", void 0);
OSPreloadContribution = (0, tslib_1.__decorate)([
    (0, inversify_1.injectable)()
], OSPreloadContribution);
exports.OSPreloadContribution = OSPreloadContribution;


/***/ },

/***/ "C:\\Users\\Julian Wiley\\Documents\\GitHub\\agentic_assistants\\frontend\\node_modules\\@theia\\core\\lib\\browser\\preload\\preload-module.js"
/*!*****************************************************************************************************************************************!*\
  !*** C:\Users\Julian Wiley\Documents\GitHub\agentic_assistants\frontend\node_modules\@theia\core\lib\browser\preload\preload-module.js ***!
  \*****************************************************************************************************************************************/
(__unused_webpack_module, exports, __webpack_require__) {


// *****************************************************************************
// Copyright (C) 2023 TypeFox and others.
//
// This program and the accompanying materials are made available under the
// terms of the Eclipse Public License v. 2.0 which is available at
// http://www.eclipse.org/legal/epl-2.0.
//
// This Source Code may also be made available under the following Secondary
```
