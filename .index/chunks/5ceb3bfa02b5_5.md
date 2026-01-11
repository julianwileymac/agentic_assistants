# Chunk: 5ceb3bfa02b5_5

- source: `frontend/browser-app/lib/frontend/vendors-C_Users_Julian_Wiley_Documents_GitHub_agentic_assistants_frontend_node_modules_theia_-001836.js`
- lines: 252-289
- chunk: 6/18

```
b */ "C:\\Users\\Julian Wiley\\Documents\\GitHub\\agentic_assistants\\frontend\\node_modules\\tslib\\tslib.es6.mjs");
const core_1 = __webpack_require__(/*! @theia/core */ "C:\\Users\\Julian Wiley\\Documents\\GitHub\\agentic_assistants\\frontend\\node_modules\\@theia\\core\\lib\\common\\index.js");
const inversify_1 = __webpack_require__(/*! @theia/core/shared/inversify */ "C:\\Users\\Julian Wiley\\Documents\\GitHub\\agentic_assistants\\frontend\\node_modules\\@theia\\core\\shared\\inversify\\index.js");
const browser_1 = __webpack_require__(/*! @theia/core/lib/browser */ "C:\\Users\\Julian Wiley\\Documents\\GitHub\\agentic_assistants\\frontend\\node_modules\\@theia\\core\\lib\\browser\\index.js");
const filepath_breadcrumb_1 = __webpack_require__(/*! ./filepath-breadcrumb */ "C:\\Users\\Julian Wiley\\Documents\\GitHub\\agentic_assistants\\frontend\\node_modules\\@theia\\filesystem\\lib\\browser\\breadcrumbs\\filepath-breadcrumb.js");
const filepath_breadcrumbs_container_1 = __webpack_require__(/*! ./filepath-breadcrumbs-container */ "C:\\Users\\Julian Wiley\\Documents\\GitHub\\agentic_assistants\\frontend\\node_modules\\@theia\\filesystem\\lib\\browser\\breadcrumbs\\filepath-breadcrumbs-container.js");
const file_tree_1 = __webpack_require__(/*! ../file-tree */ "C:\\Users\\Julian Wiley\\Documents\\GitHub\\agentic_assistants\\frontend\\node_modules\\@theia\\filesystem\\lib\\browser\\file-tree\\index.js");
const file_service_1 = __webpack_require__(/*! ../file-service */ "C:\\Users\\Julian Wiley\\Documents\\GitHub\\agentic_assistants\\frontend\\node_modules\\@theia\\filesystem\\lib\\browser\\file-service.js");
exports.FilepathBreadcrumbType = Symbol('FilepathBreadcrumb');
let FilepathBreadcrumbsContribution = class FilepathBreadcrumbsContribution {
    constructor() {
        this.onDidChangeBreadcrumbsEmitter = new core_1.Emitter();
        this.type = exports.FilepathBreadcrumbType;
        this.priority = 100;
    }
    get onDidChangeBreadcrumbs() {
        return this.onDidChangeBreadcrumbsEmitter.event;
    }
    async computeBreadcrumbs(uri) {
        if (uri.scheme !== 'file') {
            return [];
        }
        const getContainerClass = this.getContainerClassCreator(uri);
        const getIconClass = this.getIconClassCreator(uri);
        return uri.allLocations
            .map((location, index) => {
            const icon = getIconClass(location, index);
            const containerClass = getContainerClass(location, index);
            return new filepath_breadcrumb_1.FilepathBreadcrumb(location, this.labelProvider.getName(location), this.labelProvider.getLongName(location), icon, containerClass);
        })
            .filter(b => this.filterBreadcrumbs(uri, b))
            .reverse();
    }
    getContainerClassCreator(fileURI) {
        return (location, index) => location.isEqual(fileURI) ? 'file' : 'folder';
    }
    getIconClassCreator(fileURI) {
```
