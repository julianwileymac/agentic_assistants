# Chunk: cc9fe33e8daf_12

- source: `frontend/browser-app/lib/frontend/C_Users_Julian_Wiley_Documents_GitHub_agentic_assistants_frontend_packages_agentic-artifacts_-341fb0.js`
- lines: 682-728
- chunk: 13/19

```
ion (decorators, target, key, desc) {
    var c = arguments.length, r = c < 3 ? target : desc === null ? desc = Object.getOwnPropertyDescriptor(target, key) : desc, d;
    if (typeof Reflect === "object" && typeof Reflect.decorate === "function") r = Reflect.decorate(decorators, target, key, desc);
    else for (var i = decorators.length - 1; i >= 0; i--) if (d = decorators[i]) r = (c < 3 ? d(r) : c > 3 ? d(target, key, r) : d(target, key)) || r;
    return c > 3 && r && Object.defineProperty(target, key, r), r;
};
var __metadata = (this && this.__metadata) || function (k, v) {
    if (typeof Reflect === "object" && typeof Reflect.metadata === "function") return Reflect.metadata(k, v);
};
var __param = (this && this.__param) || function (paramIndex, decorator) {
    return function (target, key) { decorator(target, key, paramIndex); }
};
var ArtifactsTreeWidget_1;
Object.defineProperty(exports, "__esModule", ({ value: true }));
exports.ArtifactsTreeWidget = exports.ArtifactNode = exports.TagNode = exports.GroupNode = exports.ARTIFACTS_TREE_WIDGET_ID = void 0;
const inversify_1 = __webpack_require__(/*! @theia/core/shared/inversify */ "C:\\Users\\Julian Wiley\\Documents\\GitHub\\agentic_assistants\\frontend\\node_modules\\@theia\\core\\shared\\inversify\\index.js");
const tree_1 = __webpack_require__(/*! @theia/core/lib/browser/tree */ "C:\\Users\\Julian Wiley\\Documents\\GitHub\\agentic_assistants\\frontend\\node_modules\\@theia\\core\\lib\\browser\\tree\\index.js");
const browser_1 = __webpack_require__(/*! @theia/core/lib/browser */ "C:\\Users\\Julian Wiley\\Documents\\GitHub\\agentic_assistants\\frontend\\node_modules\\@theia\\core\\lib\\browser\\index.js");
const core_1 = __webpack_require__(/*! @theia/core */ "C:\\Users\\Julian Wiley\\Documents\\GitHub\\agentic_assistants\\frontend\\node_modules\\@theia\\core\\lib\\common\\index.js");
const artifact_service_1 = __webpack_require__(/*! ./artifact-service */ "C:\\Users\\Julian Wiley\\Documents\\GitHub\\agentic_assistants\\frontend\\packages\\agentic-artifacts\\lib\\browser\\artifact-service.js");
exports.ARTIFACTS_TREE_WIDGET_ID = 'artifacts-tree-widget';
var GroupNode;
(function (GroupNode) {
    function is(node) {
        return !!node && 'group' in node;
    }
    GroupNode.is = is;
})(GroupNode = exports.GroupNode || (exports.GroupNode = {}));
var TagNode;
(function (TagNode) {
    function is(node) {
        return !!node && 'tag' in node;
    }
    TagNode.is = is;
})(TagNode = exports.TagNode || (exports.TagNode = {}));
var ArtifactNode;
(function (ArtifactNode) {
    function is(node) {
        return !!node && 'artifact' in node;
    }
    ArtifactNode.is = is;
})(ArtifactNode = exports.ArtifactNode || (exports.ArtifactNode = {}));
let ArtifactsTreeWidget = ArtifactsTreeWidget_1 = class ArtifactsTreeWidget extends tree_1.TreeWidget {
    constructor(props, model, contextMenuRenderer) {
        super(props, model, contextMenuRenderer);
        this.props = props;
```
