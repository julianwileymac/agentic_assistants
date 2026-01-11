# Chunk: 68a15bdf9abc_0

- source: `frontend/packages/agentic-artifacts/lib/browser/artifact-commands.js`
- lines: 1-79
- chunk: 1/5

```
"use strict";
/**
 * Artifact Command Contribution
 *
 * Provides commands for artifact management.
 */
var __decorate = (this && this.__decorate) || function (decorators, target, key, desc) {
    var c = arguments.length, r = c < 3 ? target : desc === null ? desc = Object.getOwnPropertyDescriptor(target, key) : desc, d;
    if (typeof Reflect === "object" && typeof Reflect.decorate === "function") r = Reflect.decorate(decorators, target, key, desc);
    else for (var i = decorators.length - 1; i >= 0; i--) if (d = decorators[i]) r = (c < 3 ? d(r) : c > 3 ? d(target, key, r) : d(target, key)) || r;
    return c > 3 && r && Object.defineProperty(target, key, r), r;
};
var __metadata = (this && this.__metadata) || function (k, v) {
    if (typeof Reflect === "object" && typeof Reflect.metadata === "function") return Reflect.metadata(k, v);
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.ArtifactCommandContribution = exports.ArtifactCommands = void 0;
const inversify_1 = require("@theia/core/shared/inversify");
const core_1 = require("@theia/core");
const artifact_service_1 = require("./artifact-service");
var ArtifactCommands;
(function (ArtifactCommands) {
    const ARTIFACTS_CATEGORY = 'Artifacts';
    ArtifactCommands.TOGGLE_ARTIFACTS_VIEW = {
        id: 'artifacts.toggleView',
        label: 'Toggle Artifacts View',
        category: ARTIFACTS_CATEGORY
    };
    ArtifactCommands.REFRESH_ARTIFACTS = {
        id: 'artifacts.refresh',
        label: 'Refresh Artifacts',
        category: ARTIFACTS_CATEGORY
    };
    ArtifactCommands.VIEW_ALL = {
        id: 'artifacts.viewAll',
        label: 'View All Artifacts',
        category: ARTIFACTS_CATEGORY
    };
    ArtifactCommands.VIEW_BY_GROUP = {
        id: 'artifacts.viewByGroup',
        label: 'View Artifacts by Group',
        category: ARTIFACTS_CATEGORY
    };
    ArtifactCommands.VIEW_BY_TAG = {
        id: 'artifacts.viewByTag',
        label: 'View Artifacts by Tag',
        category: ARTIFACTS_CATEGORY
    };
    ArtifactCommands.VIEW_SHARED = {
        id: 'artifacts.viewShared',
        label: 'View Shared Artifacts',
        category: ARTIFACTS_CATEGORY
    };
    ArtifactCommands.ADD_TAG = {
        id: 'artifacts.addTag',
        label: 'Add Tag to Artifact',
        category: ARTIFACTS_CATEGORY
    };
    ArtifactCommands.REMOVE_TAG = {
        id: 'artifacts.removeTag',
        label: 'Remove Tag from Artifact',
        category: ARTIFACTS_CATEGORY
    };
    ArtifactCommands.ADD_TO_GROUP = {
        id: 'artifacts.addToGroup',
        label: 'Add Artifact to Group',
        category: ARTIFACTS_CATEGORY
    };
    ArtifactCommands.REMOVE_FROM_GROUP = {
        id: 'artifacts.removeFromGroup',
        label: 'Remove Artifact from Group',
        category: ARTIFACTS_CATEGORY
    };
    ArtifactCommands.SHARE_ARTIFACT = {
        id: 'artifacts.share',
        label: 'Share Artifact',
        category: ARTIFACTS_CATEGORY
    };
```
