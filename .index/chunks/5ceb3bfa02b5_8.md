# Chunk: 5ceb3bfa02b5_8

- source: `frontend/browser-app/lib/frontend/vendors-C_Users_Julian_Wiley_Documents_GitHub_agentic_assistants_frontend_node_modules_theia_-001836.js`
- lines: 380-427
- chunk: 9/18

```
\\agentic_assistants\\frontend\\node_modules\\@theia\\core\\lib\\common\\selection-command-handler.js");
const common_1 = __webpack_require__(/*! @theia/core/lib/common */ "C:\\Users\\Julian Wiley\\Documents\\GitHub\\agentic_assistants\\frontend\\node_modules\\@theia\\core\\lib\\common\\index.js");
const files_1 = __webpack_require__(/*! ../common/files */ "C:\\Users\\Julian Wiley\\Documents\\GitHub\\agentic_assistants\\frontend\\node_modules\\@theia\\filesystem\\lib\\common\\files.js");
var FileSelection;
(function (FileSelection) {
    function is(arg) {
        return (0, common_1.isObject)(arg) && files_1.FileStat.is(arg.fileStat);
    }
    FileSelection.is = is;
    class CommandHandler extends selection_command_handler_1.SelectionCommandHandler {
        constructor(selectionService, options) {
            super(selectionService, arg => FileSelection.is(arg) ? arg : undefined, options);
            this.selectionService = selectionService;
            this.options = options;
        }
    }
    FileSelection.CommandHandler = CommandHandler;
})(FileSelection = exports.FileSelection || (exports.FileSelection = {}));


/***/ },

/***/ "C:\\Users\\Julian Wiley\\Documents\\GitHub\\agentic_assistants\\frontend\\node_modules\\@theia\\filesystem\\lib\\browser\\filesystem-frontend-contribution.js"
/*!*********************************************************************************************************************************************************!*\
  !*** C:\Users\Julian Wiley\Documents\GitHub\agentic_assistants\frontend\node_modules\@theia\filesystem\lib\browser\filesystem-frontend-contribution.js ***!
  \*********************************************************************************************************************************************************/
(__unused_webpack_module, exports, __webpack_require__) {


// *****************************************************************************
// Copyright (C) 2018 TypeFox and others.
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
exports.FileSystemFrontendContribution = exports.FileSystemCommands = void 0;
const tslib_1 = __webpack_require__(/*! tslib */ "C:\\Users\\Julian Wiley\\Documents\\GitHub\\agentic_assistants\\frontend\\node_modules\\tslib\\tslib.es6.mjs");
```
