# Chunk: cc9fe33e8daf_14

- source: `frontend/browser-app/lib/frontend/C_Users_Julian_Wiley_Documents_GitHub_agentic_assistants_frontend_packages_agentic-artifacts_-341fb0.js`
- lines: 802-888
- chunk: 15/19

```
t',
            name: 'Artifacts by Group',
            parent: undefined,
            children: [],
            visible: false
        };
        // Group nodes
        const groupNodes = groups.map(group => {
            const groupArtifacts = artifacts.filter(a => a.groups.includes(group.name));
            return this.createGroupNode(group, groupArtifacts, root);
        });
        // Ungrouped artifacts
        const ungrouped = artifacts.filter(a => a.groups.length === 0);
        if (ungrouped.length > 0) {
            const ungroupedNode = {
                id: 'group-ungrouped',
                name: 'Ungrouped',
                parent: root,
                children: ungrouped.map(a => this.createArtifactNode(a, root)),
                selected: false,
                expanded: false
            };
            groupNodes.push(ungroupedNode);
        }
        root.children = groupNodes;
        return root;
    }
    createTaggedRoot() {
        const tags = this.artifactService.getTags();
        const artifacts = this.artifactService.getArtifacts();
        const root = {
            id: 'artifacts-root',
            name: 'Artifacts by Tag',
            parent: undefined,
            children: [],
            visible: false
        };
        // Tag nodes
        const tagNodes = tags.map(tag => {
            const tagArtifacts = artifacts.filter(a => a.tags.includes(tag.name));
            return this.createTagNode(tag, tagArtifacts, root);
        });
        // Untagged artifacts
        const untagged = artifacts.filter(a => a.tags.length === 0);
        if (untagged.length > 0) {
            const untaggedNode = {
                id: 'tag-untagged',
                name: 'Untagged',
                parent: root,
                children: untagged.map(a => this.createArtifactNode(a, root)),
                selected: false,
                expanded: false
            };
            tagNodes.push(untaggedNode);
        }
        root.children = tagNodes;
        return root;
    }
    createSharedRoot() {
        const artifacts = this.artifactService.getArtifacts().filter(a => a.is_shared);
        const root = {
            id: 'artifacts-root',
            name: 'Shared Artifacts',
            parent: undefined,
            children: [],
            visible: false
        };
        root.children = artifacts.map(artifact => this.createArtifactNode(artifact, root));
        return root;
    }
    createGroupNode(group, artifacts, parent) {
        const node = {
            id: `group-${group.name}`,
            name: `${group.name} (${group.artifact_count})`,
            parent,
            children: [],
            selected: false,
            expanded: false,
            group
        };
        node.children = artifacts.map(artifact => this.createArtifactNode(artifact, node));
        return node;
    }
    createTagNode(tag, artifacts, parent) {
        const node = {
            id: `tag-${tag.name}`,
```
