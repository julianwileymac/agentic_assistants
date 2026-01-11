# Chunk: cc9fe33e8daf_13

- source: `frontend/browser-app/lib/frontend/C_Users_Julian_Wiley_Documents_GitHub_agentic_assistants_frontend_packages_agentic-artifacts_-341fb0.js`
- lines: 723-811
- chunk: 14/19

```
factNode = exports.ArtifactNode || (exports.ArtifactNode = {}));
let ArtifactsTreeWidget = ArtifactsTreeWidget_1 = class ArtifactsTreeWidget extends tree_1.TreeWidget {
    constructor(props, model, contextMenuRenderer) {
        super(props, model, contextMenuRenderer);
        this.props = props;
        this.model = model;
        this.contextMenuRenderer = contextMenuRenderer;
        this.viewMode = 'all';
        this.id = ArtifactsTreeWidget_1.ID;
        this.title.label = ArtifactsTreeWidget_1.LABEL;
        this.title.caption = ArtifactsTreeWidget_1.LABEL;
        this.title.closable = true;
        this.title.iconClass = 'fa fa-archive';
    }
    init() {
        super.init();
        // Listen for artifact changes
        this.artifactService.onArtifactsChanged(() => {
            this.refreshTree();
        });
        this.artifactService.onGroupsChanged(() => {
            if (this.viewMode === 'by-group') {
                this.refreshTree();
            }
        });
        this.artifactService.onTagsChanged(() => {
            if (this.viewMode === 'by-tag') {
                this.refreshTree();
            }
        });
        // Initial load
        this.refresh();
    }
    async refresh() {
        try {
            await this.artifactService.refreshArtifacts();
            this.refreshTree();
        }
        catch (error) {
            this.messageService.error('Failed to load artifacts: ' + error);
        }
    }
    setViewMode(mode) {
        this.viewMode = mode;
        this.refreshTree();
    }
    refreshTree() {
        let root;
        switch (this.viewMode) {
            case 'by-group':
                root = this.createGroupedRoot();
                break;
            case 'by-tag':
                root = this.createTaggedRoot();
                break;
            case 'shared':
                root = this.createSharedRoot();
                break;
            default:
                root = this.createAllArtifactsRoot();
        }
        this.model.root = root;
    }
    createAllArtifactsRoot() {
        const artifacts = this.artifactService.getArtifacts();
        const root = {
            id: 'artifacts-root',
            name: 'All Artifacts',
            parent: undefined,
            children: [],
            visible: false
        };
        root.children = artifacts.map(artifact => this.createArtifactNode(artifact, root));
        return root;
    }
    createGroupedRoot() {
        const groups = this.artifactService.getGroups();
        const artifacts = this.artifactService.getArtifacts();
        const root = {
            id: 'artifacts-root',
            name: 'Artifacts by Group',
            parent: undefined,
            children: [],
            visible: false
        };
        // Group nodes
        const groupNodes = groups.map(group => {
            const groupArtifacts = artifacts.filter(a => a.groups.includes(group.name));
```
