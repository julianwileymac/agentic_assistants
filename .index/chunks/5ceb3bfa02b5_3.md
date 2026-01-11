# Chunk: 5ceb3bfa02b5_3

- source: `frontend/browser-app/lib/frontend/vendors-C_Users_Julian_Wiley_Documents_GitHub_agentic_assistants_frontend_node_modules_theia_-001836.js`
- lines: 165-217
- chunk: 4/18

```
 available at
// https://www.gnu.org/software/classpath/license.html.
//
// SPDX-License-Identifier: EPL-2.0 OR GPL-2.0-only WITH Classpath-exception-2.0
// *****************************************************************************
Object.defineProperty(exports, "__esModule", ({ value: true }));
exports.BreadcrumbsFileTreeWidget = exports.createFileTreeBreadcrumbsWidget = exports.createFileTreeBreadcrumbsContainer = void 0;
const tslib_1 = __webpack_require__(/*! tslib */ "C:\\Users\\Julian Wiley\\Documents\\GitHub\\agentic_assistants\\frontend\\node_modules\\tslib\\tslib.es6.mjs");
const inversify_1 = __webpack_require__(/*! @theia/core/shared/inversify */ "C:\\Users\\Julian Wiley\\Documents\\GitHub\\agentic_assistants\\frontend\\node_modules\\@theia\\core\\shared\\inversify\\index.js");
const browser_1 = __webpack_require__(/*! @theia/core/lib/browser */ "C:\\Users\\Julian Wiley\\Documents\\GitHub\\agentic_assistants\\frontend\\node_modules\\@theia\\core\\lib\\browser\\index.js");
const file_tree_1 = __webpack_require__(/*! ../file-tree */ "C:\\Users\\Julian Wiley\\Documents\\GitHub\\agentic_assistants\\frontend\\node_modules\\@theia\\filesystem\\lib\\browser\\file-tree\\index.js");
const BREADCRUMBS_FILETREE_CLASS = 'theia-FilepathBreadcrumbFileTree';
function createFileTreeBreadcrumbsContainer(parent) {
    const child = (0, file_tree_1.createFileTreeContainer)(parent);
    child.unbind(file_tree_1.FileTreeWidget);
    child.rebind(browser_1.TreeProps).toConstantValue({ ...browser_1.defaultTreeProps, virtualized: false });
    child.bind(BreadcrumbsFileTreeWidget).toSelf();
    return child;
}
exports.createFileTreeBreadcrumbsContainer = createFileTreeBreadcrumbsContainer;
function createFileTreeBreadcrumbsWidget(parent) {
    return createFileTreeBreadcrumbsContainer(parent).get(BreadcrumbsFileTreeWidget);
}
exports.createFileTreeBreadcrumbsWidget = createFileTreeBreadcrumbsWidget;
let BreadcrumbsFileTreeWidget = class BreadcrumbsFileTreeWidget extends file_tree_1.FileTreeWidget {
    constructor(props, model, contextMenuRenderer) {
        super(props, model, contextMenuRenderer);
        this.model = model;
        this.addClass(BREADCRUMBS_FILETREE_CLASS);
    }
    createNodeAttributes(node, props) {
        const elementAttrs = super.createNodeAttributes(node, props);
        return {
            ...elementAttrs,
            draggable: false
        };
    }
    tapNode(node) {
        if (file_tree_1.FileStatNode.is(node) && !node.fileStat.isDirectory) {
            (0, browser_1.open)(this.openerService, node.uri, { preview: true });
        }
        else {
            super.tapNode(node);
        }
    }
};
(0, tslib_1.__decorate)([
    (0, inversify_1.inject)(browser_1.OpenerService),
    (0, tslib_1.__metadata)("design:type", Object)
], BreadcrumbsFileTreeWidget.prototype, "openerService", void 0);
BreadcrumbsFileTreeWidget = (0, tslib_1.__decorate)([
    (0, inversify_1.injectable)(),
```
