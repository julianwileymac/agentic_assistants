# Chunk: 5ceb3bfa02b5_2

- source: `frontend/browser-app/lib/frontend/vendors-C_Users_Julian_Wiley_Documents_GitHub_agentic_assistants_frontend_node_modules_theia_-001836.js`
- lines: 115-171
- chunk: 3/18

```
software/classpath/license.html.
//
// SPDX-License-Identifier: EPL-2.0 OR GPL-2.0-only WITH Classpath-exception-2.0
// *****************************************************************************
Object.defineProperty(exports, "__esModule", ({ value: true }));
exports.FilepathBreadcrumb = void 0;
const filepath_breadcrumbs_contribution_1 = __webpack_require__(/*! ./filepath-breadcrumbs-contribution */ "C:\\Users\\Julian Wiley\\Documents\\GitHub\\agentic_assistants\\frontend\\node_modules\\@theia\\filesystem\\lib\\browser\\breadcrumbs\\filepath-breadcrumbs-contribution.js");
class FilepathBreadcrumb {
    constructor(uri, label, longLabel, iconClass, containerClass) {
        this.uri = uri;
        this.label = label;
        this.longLabel = longLabel;
        this.iconClass = iconClass;
        this.containerClass = containerClass;
    }
    get id() {
        return this.type.toString() + '_' + this.uri.toString();
    }
    get type() {
        return filepath_breadcrumbs_contribution_1.FilepathBreadcrumbType;
    }
}
exports.FilepathBreadcrumb = FilepathBreadcrumb;
(function (FilepathBreadcrumb) {
    function is(breadcrumb) {
        return 'uri' in breadcrumb;
    }
    FilepathBreadcrumb.is = is;
})(FilepathBreadcrumb = exports.FilepathBreadcrumb || (exports.FilepathBreadcrumb = {}));


/***/ },

/***/ "C:\\Users\\Julian Wiley\\Documents\\GitHub\\agentic_assistants\\frontend\\node_modules\\@theia\\filesystem\\lib\\browser\\breadcrumbs\\filepath-breadcrumbs-container.js"
/*!*******************************************************************************************************************************************************************!*\
  !*** C:\Users\Julian Wiley\Documents\GitHub\agentic_assistants\frontend\node_modules\@theia\filesystem\lib\browser\breadcrumbs\filepath-breadcrumbs-container.js ***!
  \*******************************************************************************************************************************************************************/
(__unused_webpack_module, exports, __webpack_require__) {


// *****************************************************************************
// Copyright (C) 2019 TypeFox and others.
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
