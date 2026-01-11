# Chunk: b34f2ec4dfb7_5

- source: `frontend/browser-app/lib/frontend/C_Users_Julian_Wiley_Documents_GitHub_agentic_assistants_frontend_packages_agentic-mlflow_lib-255529.js`
- lines: 222-291
- chunk: 6/16

```
iment is expanded
            await this.mlflowService.listRuns(node.experiment.experiment_id);
            const runs = this.mlflowService.getRuns(node.experiment.experiment_id);
            node.children = runs.map(run => this.createRunNode(run, node));
            await this.model.refresh(node);
        }
    }
    toNodeIcon(node) {
        if (ExperimentNode.is(node)) {
            return 'fa fa-flask';
        }
        if (RunNode.is(node)) {
            const status = node.run.status;
            switch (status) {
                case 'RUNNING':
                    return 'fa fa-spinner fa-spin';
                case 'FINISHED':
                    return 'fa fa-check-circle text-success';
                case 'FAILED':
                    return 'fa fa-times-circle text-error';
                case 'KILLED':
                    return 'fa fa-stop-circle text-warning';
                default:
                    return 'fa fa-circle';
            }
        }
        return '';
    }
};
ExperimentsTreeWidget.ID = exports.EXPERIMENTS_TREE_WIDGET_ID;
ExperimentsTreeWidget.LABEL = 'Experiments';
__decorate([
    (0, inversify_1.inject)(mlflow_service_1.MLFlowServiceSymbol),
    __metadata("design:type", mlflow_service_1.MLFlowService)
], ExperimentsTreeWidget.prototype, "mlflowService", void 0);
__decorate([
    (0, inversify_1.inject)(core_1.MessageService),
    __metadata("design:type", core_1.MessageService)
], ExperimentsTreeWidget.prototype, "messageService", void 0);
__decorate([
    (0, inversify_1.postConstruct)(),
    __metadata("design:type", Function),
    __metadata("design:paramtypes", []),
    __metadata("design:returntype", void 0)
], ExperimentsTreeWidget.prototype, "init", null);
ExperimentsTreeWidget = ExperimentsTreeWidget_1 = __decorate([
    (0, inversify_1.injectable)(),
    __param(0, (0, inversify_1.inject)(tree_1.TreeProps)),
    __param(1, (0, inversify_1.inject)(tree_1.TreeModel)),
    __param(2, (0, inversify_1.inject)(browser_1.ContextMenuRenderer)),
    __metadata("design:paramtypes", [Object, Object, browser_1.ContextMenuRenderer])
], ExperimentsTreeWidget);
exports.ExperimentsTreeWidget = ExperimentsTreeWidget;


/***/ },

/***/ "C:\\Users\\Julian Wiley\\Documents\\GitHub\\agentic_assistants\\frontend\\packages\\agentic-mlflow\\lib\\browser\\experiments-view-contribution.js"
/*!***********************************************************************************************************************************************!*\
  !*** C:\Users\Julian Wiley\Documents\GitHub\agentic_assistants\frontend\packages\agentic-mlflow\lib\browser\experiments-view-contribution.js ***!
  \***********************************************************************************************************************************************/
(__unused_webpack_module, exports, __webpack_require__) {


/**
 * Experiments View Contribution
 *
 * Registers the experiments tree view in the left panel.
 */
```
