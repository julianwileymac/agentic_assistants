# Chunk: daca156bbcb5_1

- source: `frontend/browser-app/lib/frontend/C_Users_Julian_Wiley_Documents_GitHub_agentic_assistants_frontend_node_modules_theia_core_lib-0053df.js`
- lines: 37-76
- chunk: 2/5

```
ers\\Julian Wiley\\Documents\\GitHub\\agentic_assistants\\frontend\\node_modules\\@theia\\core\\lib\\browser\\request\\browser-request-service.js"
/*!**************************************************************************************************************************************************!*\
  !*** C:\Users\Julian Wiley\Documents\GitHub\agentic_assistants\frontend\node_modules\@theia\core\lib\browser\request\browser-request-service.js ***!
  \**************************************************************************************************************************************************/
(__unused_webpack_module, exports, __webpack_require__) {


/********************************************************************************
 * Copyright (C) 2022 TypeFox and others.
 *
 * This program and the accompanying materials are made available under the
 * terms of the Eclipse Public License v. 2.0 which is available at
 * http://www.eclipse.org/legal/epl-2.0.
 *
 * This Source Code may also be made available under the following Secondary
 * Licenses when the conditions for such availability set forth in the Eclipse
 * Public License v. 2.0 are satisfied: GNU General Public License, version 2
 * with the GNU Classpath Exception which is available at
 * https://www.gnu.org/software/classpath/license.html.
 *
 * SPDX-License-Identifier: EPL-2.0 OR GPL-2.0-only WITH Classpath-exception-2.0
 ********************************************************************************/
Object.defineProperty(exports, "__esModule", ({ value: true }));
exports.XHRBrowserRequestService = exports.ProxyingBrowserRequestService = exports.AbstractBrowserRequestService = void 0;
const tslib_1 = __webpack_require__(/*! tslib */ "C:\\Users\\Julian Wiley\\Documents\\GitHub\\agentic_assistants\\frontend\\node_modules\\tslib\\tslib.es6.mjs");
const inversify_1 = __webpack_require__(/*! inversify */ "C:\\Users\\Julian Wiley\\Documents\\GitHub\\agentic_assistants\\frontend\\node_modules\\inversify\\lib\\cjs\\index.js");
const request_1 = __webpack_require__(/*! @theia/request */ "C:\\Users\\Julian Wiley\\Documents\\GitHub\\agentic_assistants\\frontend\\node_modules\\@theia\\request\\lib\\index.js");
const preference_service_1 = __webpack_require__(/*! ../preferences/preference-service */ "C:\\Users\\Julian Wiley\\Documents\\GitHub\\agentic_assistants\\frontend\\node_modules\\@theia\\core\\lib\\browser\\preferences\\preference-service.js");
let AbstractBrowserRequestService = class AbstractBrowserRequestService {
    constructor() {
        this.configurePromise = Promise.resolve();
    }
    init() {
        this.configurePromise = this.preferenceService.ready.then(() => {
            const proxyUrl = this.preferenceService.get('http.proxy');
            const proxyAuthorization = this.preferenceService.get('http.proxyAuthorization');
            const strictSSL = this.preferenceService.get('http.proxyStrictSSL');
            return this.configure({
                proxyUrl,
```
