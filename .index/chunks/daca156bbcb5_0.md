# Chunk: daca156bbcb5_0

- source: `frontend/browser-app/lib/frontend/C_Users_Julian_Wiley_Documents_GitHub_agentic_assistants_frontend_node_modules_theia_core_lib-0053df.js`
- lines: 1-39
- chunk: 1/5

```
"use strict";
(self["webpackChunkbrowser_app"] = self["webpackChunkbrowser_app"] || []).push([["C_Users_Julian_Wiley_Documents_GitHub_agentic_assistants_frontend_node_modules_theia_core_lib-0053df"],{

/***/ "C:\\Users\\Julian Wiley\\Documents\\GitHub\\agentic_assistants\\frontend\\node_modules\\@theia\\core\\lib\\browser\\request\\browser-request-module.js"
/*!*************************************************************************************************************************************************!*\
  !*** C:\Users\Julian Wiley\Documents\GitHub\agentic_assistants\frontend\node_modules\@theia\core\lib\browser\request\browser-request-module.js ***!
  \*************************************************************************************************************************************************/
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
const inversify_1 = __webpack_require__(/*! inversify */ "C:\\Users\\Julian Wiley\\Documents\\GitHub\\agentic_assistants\\frontend\\node_modules\\inversify\\lib\\cjs\\index.js");
const request_1 = __webpack_require__(/*! @theia/request */ "C:\\Users\\Julian Wiley\\Documents\\GitHub\\agentic_assistants\\frontend\\node_modules\\@theia\\request\\lib\\index.js");
const browser_request_service_1 = __webpack_require__(/*! ./browser-request-service */ "C:\\Users\\Julian Wiley\\Documents\\GitHub\\agentic_assistants\\frontend\\node_modules\\@theia\\core\\lib\\browser\\request\\browser-request-service.js");
exports["default"] = new inversify_1.ContainerModule(bind => {
    bind(request_1.RequestService).to(browser_request_service_1.XHRBrowserRequestService).inSingletonScope();
});


/***/ },

/***/ "C:\\Users\\Julian Wiley\\Documents\\GitHub\\agentic_assistants\\frontend\\node_modules\\@theia\\core\\lib\\browser\\request\\browser-request-service.js"
/*!**************************************************************************************************************************************************!*\
```
