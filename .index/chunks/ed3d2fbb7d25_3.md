# Chunk: ed3d2fbb7d25_3

- source: `frontend/browser-app/lib/frontend/vendors-C_Users_Julian_Wiley_Documents_GitHub_agentic_assistants_frontend_node_modules_theia_-7f5c5b.js`
- lines: 107-149
- chunk: 4/6

```
oftware/classpath/license.html.
//
// SPDX-License-Identifier: EPL-2.0 OR GPL-2.0-only WITH Classpath-exception-2.0
// *****************************************************************************
Object.defineProperty(exports, "__esModule", ({ value: true }));
exports.FileDownloadService = void 0;
const tslib_1 = __webpack_require__(/*! tslib */ "C:\\Users\\Julian Wiley\\Documents\\GitHub\\agentic_assistants\\frontend\\node_modules\\tslib\\tslib.es6.mjs");
const inversify_1 = __webpack_require__(/*! @theia/core/shared/inversify */ "C:\\Users\\Julian Wiley\\Documents\\GitHub\\agentic_assistants\\frontend\\node_modules\\@theia\\core\\shared\\inversify\\index.js");
const logger_1 = __webpack_require__(/*! @theia/core/lib/common/logger */ "C:\\Users\\Julian Wiley\\Documents\\GitHub\\agentic_assistants\\frontend\\node_modules\\@theia\\core\\lib\\common\\logger.js");
const endpoint_1 = __webpack_require__(/*! @theia/core/lib/browser/endpoint */ "C:\\Users\\Julian Wiley\\Documents\\GitHub\\agentic_assistants\\frontend\\node_modules\\@theia\\core\\lib\\browser\\endpoint.js");
const message_service_1 = __webpack_require__(/*! @theia/core/lib/common/message-service */ "C:\\Users\\Julian Wiley\\Documents\\GitHub\\agentic_assistants\\frontend\\node_modules\\@theia\\core\\lib\\common\\message-service.js");
const widgets_1 = __webpack_require__(/*! @theia/core/lib/browser/widgets */ "C:\\Users\\Julian Wiley\\Documents\\GitHub\\agentic_assistants\\frontend\\node_modules\\@theia\\core\\lib\\browser\\widgets\\index.js");
const core_1 = __webpack_require__(/*! @theia/core */ "C:\\Users\\Julian Wiley\\Documents\\GitHub\\agentic_assistants\\frontend\\node_modules\\@theia\\core\\lib\\common\\index.js");
let FileDownloadService = class FileDownloadService {
    constructor() {
        this.downloadCounter = 0;
    }
    handleCopy(event, downloadUrl) {
        if (downloadUrl && event.clipboardData) {
            event.clipboardData.setData('text/plain', downloadUrl);
            event.preventDefault();
            this.messageService.info(core_1.nls.localize('theia/filesystem/copiedToClipboard', 'Copied the download link to the clipboard.'));
        }
    }
    async cancelDownload(id) {
        await fetch(`${this.endpoint()}/download/?id=${id}&cancel=true`);
    }
    async download(uris, options) {
        let cancel = false;
        if (uris.length === 0) {
            return;
        }
        const copyLink = options && options.copyLink ? true : false;
        try {
            const text = copyLink ?
                core_1.nls.localize('theia/filesystem/prepareDownloadLink', 'Preparing download link...') :
                core_1.nls.localize('theia/filesystem/prepareDownload', 'Preparing download...');
            const [progress, result] = await Promise.all([
                this.messageService.showProgress({
                    text: text,
                    options: { cancelable: true }
                }, () => { cancel = true; }),
```
