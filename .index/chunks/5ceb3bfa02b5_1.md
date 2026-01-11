# Chunk: 5ceb3bfa02b5_1

- source: `frontend/browser-app/lib/frontend/vendors-C_Users_Julian_Wiley_Documents_GitHub_agentic_assistants_frontend_node_modules_theia_-001836.js`
- lines: 51-121
- chunk: 2/18

```
       if (givenSelection) {
            return this.isMulti() ? [givenSelection] : givenSelection;
        }
        const globalSelection = this.getSingleSelection(this.selectionService.selection);
        if (this.isMulti()) {
            return this.getMultiSelection(globalSelection);
        }
        return this.getSingleSelection(globalSelection);
    }
    getSingleSelection(arg) {
        let selection = this.toSelection(arg);
        if (selection) {
            return selection;
        }
        if (Array.isArray(arg)) {
            for (const element of arg) {
                selection = this.toSelection(element);
                if (selection) {
                    return selection;
                }
            }
        }
        return undefined;
    }
    getMultiSelection(arg) {
        let selection = this.toSelection(arg);
        if (selection) {
            return [selection];
        }
        const result = [];
        if (Array.isArray(arg)) {
            for (const element of arg) {
                selection = this.toSelection(element);
                if (selection) {
                    result.push(selection);
                }
            }
        }
        return result.length ? result : undefined;
    }
}
exports.SelectionCommandHandler = SelectionCommandHandler;


/***/ },

/***/ "C:\\Users\\Julian Wiley\\Documents\\GitHub\\agentic_assistants\\frontend\\node_modules\\@theia\\filesystem\\lib\\browser\\breadcrumbs\\filepath-breadcrumb.js"
/*!********************************************************************************************************************************************************!*\
  !*** C:\Users\Julian Wiley\Documents\GitHub\agentic_assistants\frontend\node_modules\@theia\filesystem\lib\browser\breadcrumbs\filepath-breadcrumb.js ***!
  \********************************************************************************************************************************************************/
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
exports.FilepathBreadcrumb = void 0;
```
