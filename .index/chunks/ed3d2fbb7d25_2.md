# Chunk: ed3d2fbb7d25_2

- source: `frontend/browser-app/lib/frontend/vendors-C_Users_Julian_Wiley_Documents_GitHub_agentic_assistants_frontend_node_modules_theia_-7f5c5b.js`
- lines: 61-113
- chunk: 3/6

```
ile_download_service_1.FileDownloadService),
    (0, tslib_1.__metadata)("design:type", file_download_service_1.FileDownloadService)
], FileDownloadCommandContribution.prototype, "downloadService", void 0);
(0, tslib_1.__decorate)([
    (0, inversify_1.inject)(selection_service_1.SelectionService),
    (0, tslib_1.__metadata)("design:type", selection_service_1.SelectionService)
], FileDownloadCommandContribution.prototype, "selectionService", void 0);
FileDownloadCommandContribution = (0, tslib_1.__decorate)([
    (0, inversify_1.injectable)()
], FileDownloadCommandContribution);
exports.FileDownloadCommandContribution = FileDownloadCommandContribution;
var FileDownloadCommands;
(function (FileDownloadCommands) {
    FileDownloadCommands.DOWNLOAD = command_1.Command.toDefaultLocalizedCommand({
        id: 'file.download',
        category: browser_2.CommonCommands.FILE_CATEGORY,
        label: 'Download'
    });
    FileDownloadCommands.COPY_DOWNLOAD_LINK = command_1.Command.toLocalizedCommand({
        id: 'file.copyDownloadLink',
        category: browser_2.CommonCommands.FILE_CATEGORY,
        label: 'Copy Download Link'
    }, 'theia/filesystem/copyDownloadLink', browser_2.CommonCommands.FILE_CATEGORY_KEY);
})(FileDownloadCommands = exports.FileDownloadCommands || (exports.FileDownloadCommands = {}));


/***/ },

/***/ "C:\\Users\\Julian Wiley\\Documents\\GitHub\\agentic_assistants\\frontend\\node_modules\\@theia\\filesystem\\lib\\browser\\download\\file-download-service.js"
/*!*******************************************************************************************************************************************************!*\
  !*** C:\Users\Julian Wiley\Documents\GitHub\agentic_assistants\frontend\node_modules\@theia\filesystem\lib\browser\download\file-download-service.js ***!
  \*******************************************************************************************************************************************************/
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
exports.FileDownloadService = void 0;
```
