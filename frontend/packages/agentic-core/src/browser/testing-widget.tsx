/**
 * Testing Widget
 *
 * Provides a lightweight test runner UI in Theia.
 */

import * as React from '@theia/core/shared/react';
import { injectable, inject, postConstruct } from '@theia/core/shared/inversify';
import { ReactWidget } from '@theia/core/lib/browser/widgets/react-widget';
import { MessageService } from '@theia/core';

import { AgenticBackendService, AgenticBackendServiceSymbol } from './agentic-backend-service';

export const TESTING_WIDGET_ID = 'agentic-testing-widget';

type TestingViewProps = {
    backendService: AgenticBackendService;
    messageService: MessageService;
};

const panelStyles: React.CSSProperties = {
    padding: '16px',
    display: 'flex',
    flexDirection: 'column',
    gap: '12px'
};

const labelStyles: React.CSSProperties = {
    fontWeight: 600,
    fontSize: '12px',
    textTransform: 'uppercase',
    opacity: 0.7
};

const inputStyles: React.CSSProperties = {
    width: '100%',
    padding: '8px',
    borderRadius: '6px',
    border: '1px solid var(--theia-border-color)',
    background: 'var(--theia-input-background)',
    color: 'var(--theia-input-foreground)'
};

const textareaStyles: React.CSSProperties = {
    ...inputStyles,
    minHeight: '160px',
    fontFamily: 'monospace',
    fontSize: '12px'
};

const buttonStyles: React.CSSProperties = {
    padding: '8px 12px',
    borderRadius: '6px',
    border: 'none',
    background: 'var(--theia-button-background)',
    color: 'var(--theia-button-foreground)',
    cursor: 'pointer'
};

const TestingView: React.FC<TestingViewProps> = ({ backendService, messageService }) => {
    const [code, setCode] = React.useState('result = 2 + 2');
    const [output, setOutput] = React.useState('');
    const [status, setStatus] = React.useState('idle');
    const [trackingEnabled, setTrackingEnabled] = React.useState(false);
    const [agentEvalEnabled, setAgentEvalEnabled] = React.useState(false);
    const [rlMetricsEnabled, setRlMetricsEnabled] = React.useState(false);
    const [lintIssues, setLintIssues] = React.useState<string[]>([]);

    const runTest = async () => {
        setStatus('running');
        setLintIssues([]);
        const response = await backendService.runTest({
            code,
            language: 'python',
            tracking_enabled: trackingEnabled,
            agent_eval_enabled: agentEvalEnabled,
            rl_metrics_enabled: rlMetricsEnabled
        });
        if (response.data) {
            const data = response.data as any;
            const primary = data.results?.[0];
            setOutput(primary?.output || JSON.stringify(data, null, 2));
            setStatus(data.run?.status || 'completed');
            messageService.info('Test run completed');
        } else {
            setOutput(response.error || 'Test run failed');
            setStatus('failed');
            messageService.error('Test run failed');
        }
    };

    const lintCode = async () => {
        const response = await backendService.lintCode({ code, language: 'python' });
        if (response.data) {
            const data = response.data as any;
            setLintIssues(data.issues || []);
            if (data.issues?.length) {
                messageService.warn('Lint issues detected');
            } else {
                messageService.info('No lint issues found');
            }
        } else {
            messageService.error(response.error || 'Lint failed');
        }
    };

    return (
        <div style={panelStyles}>
            <div>
                <div style={labelStyles}>Test Code</div>
                <textarea
                    style={textareaStyles}
                    value={code}
                    onChange={(e) => setCode(e.target.value)}
                />
            </div>
            <div style={{ display: 'flex', gap: '12px', flexWrap: 'wrap' }}>
                <label style={{ display: 'flex', gap: '6px', alignItems: 'center' }}>
                    <input
                        type="checkbox"
                        checked={trackingEnabled}
                        onChange={(e) => setTrackingEnabled(e.target.checked)}
                    />
                    Tracking
                </label>
                <label style={{ display: 'flex', gap: '6px', alignItems: 'center' }}>
                    <input
                        type="checkbox"
                        checked={agentEvalEnabled}
                        onChange={(e) => setAgentEvalEnabled(e.target.checked)}
                    />
                    Agent Eval
                </label>
                <label style={{ display: 'flex', gap: '6px', alignItems: 'center' }}>
                    <input
                        type="checkbox"
                        checked={rlMetricsEnabled}
                        onChange={(e) => setRlMetricsEnabled(e.target.checked)}
                    />
                    RL Metrics
                </label>
            </div>
            <div style={{ display: 'flex', gap: '12px' }}>
                <button style={buttonStyles} onClick={runTest} disabled={!code.trim()}>
                    Run Test
                </button>
                <button style={buttonStyles} onClick={lintCode} disabled={!code.trim()}>
                    Lint
                </button>
            </div>
            {lintIssues.length > 0 && (
                <div>
                    <div style={labelStyles}>Lint Issues</div>
                    <ul>
                        {lintIssues.map((issue, idx) => (
                            <li key={idx}>{issue}</li>
                        ))}
                    </ul>
                </div>
            )}
            <div>
                <div style={labelStyles}>Output ({status})</div>
                <pre style={{ ...textareaStyles, whiteSpace: 'pre-wrap' }}>{output || 'No output yet.'}</pre>
            </div>
        </div>
    );
};

@injectable()
export class TestingWidget extends ReactWidget {
    static readonly ID = TESTING_WIDGET_ID;
    static readonly LABEL = 'Testing';

    @inject(AgenticBackendServiceSymbol)
    protected readonly backendService: AgenticBackendService;

    @inject(MessageService)
    protected readonly messageService: MessageService;

    @postConstruct()
    protected init(): void {
        this.id = TestingWidget.ID;
        this.title.label = TestingWidget.LABEL;
        this.title.caption = TestingWidget.LABEL;
        this.title.closable = true;
        this.update();
    }

    protected render(): React.ReactNode {
        return (
            <TestingView
                backendService={this.backendService}
                messageService={this.messageService}
            />
        );
    }
}
