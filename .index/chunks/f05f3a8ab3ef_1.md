# Chunk: f05f3a8ab3ef_1

- source: `frontend/packages/agentic-core/lib/browser/agentic-commands.js`
- lines: 63-129
- chunk: 2/3

```
.CHECK_CONNECTION, {
            execute: async () => {
                const connected = await this.backendService.checkConnection();
                if (connected) {
                    this.messageService.info('Successfully connected to Agentic backend');
                }
                else {
                    this.messageService.error('Failed to connect to Agentic backend');
                }
            }
        });
        registry.registerCommand(AgenticCommands.SHOW_CONFIG, {
            execute: async () => {
                const response = await this.backendService.getConfig();
                if (response.data) {
                    console.log('Agentic Configuration:', response.data);
                    this.messageService.info('Configuration logged to console');
                }
                else {
                    this.messageService.error('Failed to fetch configuration: ' + response.error);
                }
            }
        });
        registry.registerCommand(AgenticCommands.LIST_EXPERIMENTS, {
            execute: async () => {
                const response = await this.backendService.listExperiments();
                if (response.data) {
                    console.log('Experiments:', response.data);
                    this.messageService.info('Experiments logged to console');
                }
                else {
                    this.messageService.error('Failed to list experiments: ' + response.error);
                }
            }
        });
        registry.registerCommand(AgenticCommands.CREATE_EXPERIMENT, {
            execute: async () => {
                const name = 'New Experiment ' + new Date().toISOString();
                const response = await this.backendService.createExperiment(name);
                if (response.data) {
                    this.messageService.info('Created experiment: ' + name);
                }
                else {
                    this.messageService.error('Failed to create experiment: ' + response.error);
                }
            }
        });
        registry.registerCommand(AgenticCommands.LIST_SESSIONS, {
            execute: async () => {
                const response = await this.backendService.listSessions();
                if (response.data) {
                    console.log('Sessions:', response.data);
                    this.messageService.info('Sessions logged to console');
                }
                else {
                    this.messageService.error('Failed to list sessions: ' + response.error);
                }
            }
        });
        registry.registerCommand(AgenticCommands.CREATE_SESSION, {
            execute: async () => {
                const name = 'New Session ' + new Date().toISOString();
                const response = await this.backendService.createSession(name);
                if (response.data) {
                    this.messageService.info('Created session: ' + name);
                }
```
