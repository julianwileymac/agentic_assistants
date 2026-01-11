# Chunk: 5ceb3bfa02b5_0

- source: `frontend/browser-app/lib/frontend/vendors-C_Users_Julian_Wiley_Documents_GitHub_agentic_assistants_frontend_node_modules_theia_-001836.js`
- lines: 1-58
- chunk: 1/18

```
"use strict";
(self["webpackChunkbrowser_app"] = self["webpackChunkbrowser_app"] || []).push([["vendors-C_Users_Julian_Wiley_Documents_GitHub_agentic_assistants_frontend_node_modules_theia_-001836"],{

/***/ "C:\\Users\\Julian Wiley\\Documents\\GitHub\\agentic_assistants\\frontend\\node_modules\\@theia\\core\\lib\\common\\selection-command-handler.js"
/*!*******************************************************************************************************************************************!*\
  !*** C:\Users\Julian Wiley\Documents\GitHub\agentic_assistants\frontend\node_modules\@theia\core\lib\common\selection-command-handler.js ***!
  \*******************************************************************************************************************************************/
(__unused_webpack_module, exports) {


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
exports.SelectionCommandHandler = void 0;
class SelectionCommandHandler {
    constructor(selectionService, toSelection, options) {
        this.selectionService = selectionService;
        this.toSelection = toSelection;
        this.options = options;
    }
    execute(...args) {
        const selection = this.getSelection(...args);
        return selection ? this.options.execute(selection, ...args) : undefined;
    }
    isVisible(...args) {
        const selection = this.getSelection(...args);
        return !!selection && (!this.options.isVisible || this.options.isVisible(selection, ...args));
    }
    isEnabled(...args) {
        const selection = this.getSelection(...args);
        return !!selection && (!this.options.isEnabled || this.options.isEnabled(selection, ...args));
    }
    isMulti() {
        return this.options && !!this.options.multi;
    }
    getSelection(...args) {
        const givenSelection = args.length && this.toSelection(args[0]);
        if (givenSelection) {
            return this.isMulti() ? [givenSelection] : givenSelection;
        }
        const globalSelection = this.getSingleSelection(this.selectionService.selection);
        if (this.isMulti()) {
            return this.getMultiSelection(globalSelection);
        }
```
