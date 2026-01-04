/**
 * Experiments Tree Widget
 * 
 * Provides a tree view for browsing MLFlow experiments and runs.
 */

import { injectable, inject, postConstruct } from '@theia/core/shared/inversify';
import { TreeWidget, TreeNode, CompositeTreeNode, SelectableTreeNode, ExpandableTreeNode, TreeModel, TreeProps } from '@theia/core/lib/browser/tree';
import { ContextMenuRenderer } from '@theia/core/lib/browser';
import { MessageService } from '@theia/core';
import { MLFlowService, MLFlowServiceSymbol, Experiment, Run } from './mlflow-service';

export const EXPERIMENTS_TREE_WIDGET_ID = 'experiments-tree-widget';

export interface ExperimentNode extends CompositeTreeNode, SelectableTreeNode, ExpandableTreeNode {
    experiment: Experiment;
}

export interface RunNode extends SelectableTreeNode {
    run: Run;
}

export namespace ExperimentNode {
    export function is(node: TreeNode | undefined): node is ExperimentNode {
        return !!node && 'experiment' in node;
    }
}

export namespace RunNode {
    export function is(node: TreeNode | undefined): node is RunNode {
        return !!node && 'run' in node;
    }
}

@injectable()
export class ExperimentsTreeWidget extends TreeWidget {

    static readonly ID = EXPERIMENTS_TREE_WIDGET_ID;
    static readonly LABEL = 'Experiments';

    @inject(MLFlowServiceSymbol)
    protected readonly mlflowService: MLFlowService;

    @inject(MessageService)
    protected readonly messageService: MessageService;

    constructor(
        @inject(TreeProps) readonly props: TreeProps,
        @inject(TreeModel) readonly model: TreeModel,
        @inject(ContextMenuRenderer) readonly contextMenuRenderer: ContextMenuRenderer
    ) {
        super(props, model, contextMenuRenderer);

        this.id = ExperimentsTreeWidget.ID;
        this.title.label = ExperimentsTreeWidget.LABEL;
        this.title.caption = ExperimentsTreeWidget.LABEL;
        this.title.closable = true;
        this.title.iconClass = 'fa fa-flask';
    }

    @postConstruct()
    protected init(): void {
        super.init();
        
        this.toDispose.push(this.model.onExpansionChanged(async node => this.handleNodeExpansion(node)));

        // Listen for experiment changes
        this.mlflowService.onExperimentsChanged(experiments => {
            this.refreshTree();
        });

        this.mlflowService.onRunsChanged(({ experimentId, runs }) => {
            this.updateExperimentRuns(experimentId, runs);
        });

        // Initial load
        this.refresh();
    }

    async refresh(): Promise<void> {
        try {
            await this.mlflowService.refreshExperiments();
            this.refreshTree();
        } catch (error) {
            this.messageService.error('Failed to load experiments: ' + error);
        }
    }

    protected refreshTree(): void {
        const experiments = this.mlflowService.getExperiments();
        const root = this.createRootNode(experiments);
        this.model.root = root;
    }

    protected createRootNode(experiments: Experiment[]): CompositeTreeNode {
        const root: CompositeTreeNode = {
            id: 'experiments-root',
            name: 'Experiments',
            parent: undefined,
            children: [],
            visible: false
        };

        const experimentNodes = experiments.map(exp => this.createExperimentNode(exp, root));
        root.children = experimentNodes;

        return root;
    }

    protected createExperimentNode(experiment: Experiment, parent: CompositeTreeNode): ExperimentNode {
        const runs = this.mlflowService.getRuns(experiment.experiment_id);
        
        const node: ExperimentNode = {
            id: `experiment-${experiment.experiment_id}`,
            name: experiment.name,
            parent,
            children: [],
            selected: false,
            expanded: false,
            experiment
        };

        node.children = runs.map(run => this.createRunNode(run, node));

        return node;
    }

    protected createRunNode(run: Run, parent: ExperimentNode): RunNode {
        return {
            id: `run-${run.run_id}`,
            name: run.run_name || run.run_id.substring(0, 8),
            parent,
            selected: false,
            run
        };
    }

    protected updateExperimentRuns(experimentId: string, runs: Run[]): void {
        const root = this.model.root;
        if (CompositeTreeNode.is(root)) {
            const experimentNode = root.children.find(
                child => ExperimentNode.is(child) && child.experiment.experiment_id === experimentId
            ) as ExperimentNode | undefined;

            if (experimentNode) {
                experimentNode.children = runs.map(run => this.createRunNode(run, experimentNode));
                this.model.refresh();
            }
        }
    }

    protected async handleNodeExpansion(node: ExpandableTreeNode): Promise<void> {
        if (!node.expanded) {
            return;
        }

        if (ExperimentNode.is(node) && node.children.length === 0) {
            // Load runs when experiment is expanded
            await this.mlflowService.listRuns(node.experiment.experiment_id);
            const runs = this.mlflowService.getRuns(node.experiment.experiment_id);
            (node as ExperimentNode).children = runs.map(run => this.createRunNode(run, node as ExperimentNode));
            await this.model.refresh(node);
        }
    }

    protected override toNodeIcon(node: TreeNode): string {
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
}

