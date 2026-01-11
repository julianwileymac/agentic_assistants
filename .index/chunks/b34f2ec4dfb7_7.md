# Chunk: b34f2ec4dfb7_7

- source: `frontend/browser-app/lib/frontend/C_Users_Julian_Wiley_Documents_GitHub_agentic_assistants_frontend_packages_agentic-mlflow_lib-255529.js`
- lines: 323-376
- chunk: 8/16

```
le)(),
    __metadata("design:paramtypes", [])
], ExperimentsViewContribution);
exports.ExperimentsViewContribution = ExperimentsViewContribution;


/***/ },

/***/ "C:\\Users\\Julian Wiley\\Documents\\GitHub\\agentic_assistants\\frontend\\packages\\agentic-mlflow\\lib\\browser\\mlflow-commands.js"
/*!*********************************************************************************************************************************!*\
  !*** C:\Users\Julian Wiley\Documents\GitHub\agentic_assistants\frontend\packages\agentic-mlflow\lib\browser\mlflow-commands.js ***!
  \*********************************************************************************************************************************/
(__unused_webpack_module, exports, __webpack_require__) {


/**
 * MLFlow Command Contribution
 *
 * Provides commands for MLFlow experiment management.
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
Object.defineProperty(exports, "__esModule", ({ value: true }));
exports.MLFlowCommandContribution = exports.MLFlowCommands = void 0;
const inversify_1 = __webpack_require__(/*! @theia/core/shared/inversify */ "C:\\Users\\Julian Wiley\\Documents\\GitHub\\agentic_assistants\\frontend\\node_modules\\@theia\\core\\shared\\inversify\\index.js");
const core_1 = __webpack_require__(/*! @theia/core */ "C:\\Users\\Julian Wiley\\Documents\\GitHub\\agentic_assistants\\frontend\\node_modules\\@theia\\core\\lib\\common\\index.js");
const mlflow_service_1 = __webpack_require__(/*! ./mlflow-service */ "C:\\Users\\Julian Wiley\\Documents\\GitHub\\agentic_assistants\\frontend\\packages\\agentic-mlflow\\lib\\browser\\mlflow-service.js");
var MLFlowCommands;
(function (MLFlowCommands) {
    const MLFLOW_CATEGORY = 'MLFlow';
    MLFlowCommands.TOGGLE_EXPERIMENTS_VIEW = {
        id: 'mlflow.toggleExperimentsView',
        label: 'Toggle Experiments View',
        category: MLFLOW_CATEGORY
    };
    MLFlowCommands.REFRESH_EXPERIMENTS = {
        id: 'mlflow.refreshExperiments',
        label: 'Refresh Experiments',
        category: MLFLOW_CATEGORY
    };
    MLFlowCommands.CREATE_EXPERIMENT = {
        id: 'mlflow.createExperiment',
        label: 'Create Experiment',
        category: MLFLOW_CATEGORY
    };
    MLFlowCommands.DELETE_EXPERIMENT = {
```
