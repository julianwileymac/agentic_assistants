# Chunk: ed3d2fbb7d25_1

- source: `frontend/browser-app/lib/frontend/vendors-C_Users_Julian_Wiley_Documents_GitHub_agentic_assistants_frontend_node_modules_theia_-7f5c5b.js`
- lines: 30-66
- chunk: 2/6

```
ser\\browser.js");
const environment_1 = __webpack_require__(/*! @theia/core/shared/@theia/application-package/lib/environment */ "C:\\Users\\Julian Wiley\\Documents\\GitHub\\agentic_assistants\\frontend\\node_modules\\@theia\\core\\shared\\@theia\\application-package\\lib\\environment\\index.js");
const selection_service_1 = __webpack_require__(/*! @theia/core/lib/common/selection-service */ "C:\\Users\\Julian Wiley\\Documents\\GitHub\\agentic_assistants\\frontend\\node_modules\\@theia\\core\\lib\\common\\selection-service.js");
const command_1 = __webpack_require__(/*! @theia/core/lib/common/command */ "C:\\Users\\Julian Wiley\\Documents\\GitHub\\agentic_assistants\\frontend\\node_modules\\@theia\\core\\lib\\common\\command.js");
const uri_command_handler_1 = __webpack_require__(/*! @theia/core/lib/common/uri-command-handler */ "C:\\Users\\Julian Wiley\\Documents\\GitHub\\agentic_assistants\\frontend\\node_modules\\@theia\\core\\lib\\common\\uri-command-handler.js");
const file_download_service_1 = __webpack_require__(/*! ./file-download-service */ "C:\\Users\\Julian Wiley\\Documents\\GitHub\\agentic_assistants\\frontend\\node_modules\\@theia\\filesystem\\lib\\browser\\download\\file-download-service.js");
const browser_2 = __webpack_require__(/*! @theia/core/lib/browser */ "C:\\Users\\Julian Wiley\\Documents\\GitHub\\agentic_assistants\\frontend\\node_modules\\@theia\\core\\lib\\browser\\index.js");
let FileDownloadCommandContribution = class FileDownloadCommandContribution {
    registerCommands(registry) {
        registry.registerCommand(FileDownloadCommands.DOWNLOAD, uri_command_handler_1.UriAwareCommandHandler.MultiSelect(this.selectionService, {
            execute: uris => this.executeDownload(uris),
            isEnabled: uris => this.isDownloadEnabled(uris),
            isVisible: uris => this.isDownloadVisible(uris),
        }));
        registry.registerCommand(FileDownloadCommands.COPY_DOWNLOAD_LINK, uri_command_handler_1.UriAwareCommandHandler.MultiSelect(this.selectionService, {
            execute: uris => this.executeDownload(uris, { copyLink: true }),
            isEnabled: uris => browser_1.isChrome && this.isDownloadEnabled(uris),
            isVisible: uris => browser_1.isChrome && this.isDownloadVisible(uris),
        }));
    }
    async executeDownload(uris, options) {
        this.downloadService.download(uris, options);
    }
    isDownloadEnabled(uris) {
        return !environment_1.environment.electron.is() && uris.length > 0 && uris.every(u => u.scheme === 'file');
    }
    isDownloadVisible(uris) {
        return this.isDownloadEnabled(uris);
    }
};
(0, tslib_1.__decorate)([
    (0, inversify_1.inject)(file_download_service_1.FileDownloadService),
    (0, tslib_1.__metadata)("design:type", file_download_service_1.FileDownloadService)
], FileDownloadCommandContribution.prototype, "downloadService", void 0);
(0, tslib_1.__decorate)([
    (0, inversify_1.inject)(selection_service_1.SelectionService),
```
