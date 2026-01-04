/**
 * Agentic WebSocket Client
 * 
 * Provides real-time event streaming from the Python backend.
 */

import { injectable } from '@theia/core/shared/inversify';
import { Emitter, Event, Disposable } from '@theia/core/lib/common';

export const AgenticWebSocketClientSymbol = Symbol('AgenticWebSocketClient');

export interface WSMessage {
    id: string;
    type: string;
    timestamp: string;
    data: Record<string, unknown>;
    source: string;
}

export interface WSCommand {
    id?: string;
    command: string;
    params: Record<string, unknown>;
}

export enum EventType {
    // Connection events
    CONNECTED = 'connected',
    DISCONNECTED = 'disconnected',
    PING = 'ping',
    PONG = 'pong',

    // Experiment events
    EXPERIMENT_CREATED = 'experiment.created',
    EXPERIMENT_UPDATED = 'experiment.updated',
    EXPERIMENT_DELETED = 'experiment.deleted',
    RUN_STARTED = 'run.started',
    RUN_ENDED = 'run.ended',
    RUN_LOG = 'run.log',
    METRICS_LOGGED = 'metrics.logged',

    // Artifact events
    ARTIFACT_CREATED = 'artifact.created',
    ARTIFACT_UPDATED = 'artifact.updated',
    ARTIFACT_DELETED = 'artifact.deleted',
    ARTIFACT_SHARED = 'artifact.shared',

    // Session events
    SESSION_CREATED = 'session.created',
    SESSION_ACTIVATED = 'session.activated',
    SESSION_DELETED = 'session.deleted',

    // System events
    CONFIG_CHANGED = 'config.changed',
    ERROR = 'error',
    NOTIFICATION = 'notification',
}

@injectable()
export class AgenticWebSocketClient implements Disposable {

    protected socket: WebSocket | undefined;
    protected connectionId: string | undefined;
    protected reconnectAttempts = 0;
    protected maxReconnectAttempts = 5;
    protected reconnectDelay = 1000;
    protected pingInterval: NodeJS.Timeout | undefined;
    protected subscriptions: Set<string> = new Set();

    protected wsUrl = 'ws://localhost:8080/ws';

    protected readonly onConnectedEmitter = new Emitter<string>();
    readonly onConnected: Event<string> = this.onConnectedEmitter.event;

    protected readonly onDisconnectedEmitter = new Emitter<void>();
    readonly onDisconnected: Event<void> = this.onDisconnectedEmitter.event;

    protected readonly onMessageEmitter = new Emitter<WSMessage>();
    readonly onMessage: Event<WSMessage> = this.onMessageEmitter.event;

    protected readonly onErrorEmitter = new Emitter<Error>();
    readonly onError: Event<Error> = this.onErrorEmitter.event;

    // Event-specific emitters
    protected readonly onExperimentEventEmitter = new Emitter<WSMessage>();
    readonly onExperimentEvent: Event<WSMessage> = this.onExperimentEventEmitter.event;

    protected readonly onArtifactEventEmitter = new Emitter<WSMessage>();
    readonly onArtifactEvent: Event<WSMessage> = this.onArtifactEventEmitter.event;

    protected readonly onSessionEventEmitter = new Emitter<WSMessage>();
    readonly onSessionEvent: Event<WSMessage> = this.onSessionEventEmitter.event;

    protected readonly onRunLogEmitter = new Emitter<WSMessage>();
    readonly onRunLog: Event<WSMessage> = this.onRunLogEmitter.event;

    protected readonly onNotificationEmitter = new Emitter<WSMessage>();
    readonly onNotification: Event<WSMessage> = this.onNotificationEmitter.event;

    /**
     * Configure the WebSocket URL
     */
    configure(url: string): void {
        this.wsUrl = url;
    }

    /**
     * Connect to the WebSocket server
     */
    async connect(clientId?: string): Promise<void> {
        if (this.socket && this.socket.readyState === WebSocket.OPEN) {
            return;
        }

        const url = clientId ? `${this.wsUrl}/${clientId}` : this.wsUrl;

        return new Promise((resolve, reject) => {
            try {
                this.socket = new WebSocket(url);

                this.socket.onopen = () => {
                    this.reconnectAttempts = 0;
                    this.startPing();
                    resolve();
                };

                this.socket.onmessage = (event) => {
                    this.handleMessage(event.data);
                };

                this.socket.onerror = (event) => {
                    const error = new Error('WebSocket error');
                    this.onErrorEmitter.fire(error);
                    reject(error);
                };

                this.socket.onclose = () => {
                    this.stopPing();
                    this.onDisconnectedEmitter.fire();
                    this.attemptReconnect();
                };
            } catch (error) {
                reject(error);
            }
        });
    }

    /**
     * Disconnect from the WebSocket server
     */
    disconnect(): void {
        this.stopPing();
        if (this.socket) {
            this.socket.close();
            this.socket = undefined;
        }
        this.connectionId = undefined;
        this.subscriptions.clear();
    }

    /**
     * Check if connected
     */
    isConnected(): boolean {
        return this.socket?.readyState === WebSocket.OPEN;
    }

    /**
     * Send a command to the server
     */
    send(command: WSCommand): void {
        if (!this.isConnected()) {
            throw new Error('WebSocket is not connected');
        }

        this.socket!.send(JSON.stringify(command));
    }

    /**
     * Subscribe to a topic
     */
    subscribe(topic: string): void {
        this.subscriptions.add(topic);
        if (this.isConnected()) {
            this.send({
                command: 'subscribe',
                params: { topic }
            });
        }
    }

    /**
     * Unsubscribe from a topic
     */
    unsubscribe(topic: string): void {
        this.subscriptions.delete(topic);
        if (this.isConnected()) {
            this.send({
                command: 'unsubscribe',
                params: { topic }
            });
        }
    }

    /**
     * Handle incoming messages
     */
    protected handleMessage(data: string): void {
        try {
            const message: WSMessage = JSON.parse(data);
            this.onMessageEmitter.fire(message);

            // Route to specific emitters based on event type
            switch (message.type) {
                case EventType.CONNECTED:
                    this.connectionId = message.data.connection_id as string;
                    this.onConnectedEmitter.fire(this.connectionId);
                    // Re-subscribe to topics after reconnect
                    this.resubscribe();
                    break;

                case EventType.PING:
                    // Server-initiated ping, respond with pong to keep connection alive
                    this.sendPong();
                    break;

                case EventType.PONG:
                    // Response to our ping, connection is healthy
                    // No action needed, the ping interval handles keepalive
                    break;

                case EventType.EXPERIMENT_CREATED:
                case EventType.EXPERIMENT_UPDATED:
                case EventType.EXPERIMENT_DELETED:
                case EventType.RUN_STARTED:
                case EventType.RUN_ENDED:
                case EventType.METRICS_LOGGED:
                    this.onExperimentEventEmitter.fire(message);
                    break;

                case EventType.RUN_LOG:
                    this.onRunLogEmitter.fire(message);
                    break;

                case EventType.ARTIFACT_CREATED:
                case EventType.ARTIFACT_UPDATED:
                case EventType.ARTIFACT_DELETED:
                case EventType.ARTIFACT_SHARED:
                    this.onArtifactEventEmitter.fire(message);
                    break;

                case EventType.SESSION_CREATED:
                case EventType.SESSION_ACTIVATED:
                case EventType.SESSION_DELETED:
                    this.onSessionEventEmitter.fire(message);
                    break;

                case EventType.NOTIFICATION:
                case EventType.ERROR:
                    this.onNotificationEmitter.fire(message);
                    break;
            }
        } catch (error) {
            console.error('Failed to parse WebSocket message:', error);
        }
    }

    /**
     * Send pong response to server ping
     */
    protected sendPong(): void {
        if (this.isConnected()) {
            try {
                this.send({ command: 'pong', params: {} });
            } catch (error) {
                console.error('Failed to send pong:', error);
            }
        }
    }

    /**
     * Re-subscribe to all topics after reconnect
     */
    protected resubscribe(): void {
        for (const topic of this.subscriptions) {
            this.send({
                command: 'subscribe',
                params: { topic }
            });
        }
    }

    /**
     * Start ping interval
     */
    protected startPing(): void {
        this.pingInterval = setInterval(() => {
            if (this.isConnected()) {
                this.send({ command: 'ping', params: {} });
            }
        }, 30000); // Ping every 30 seconds
    }

    /**
     * Stop ping interval
     */
    protected stopPing(): void {
        if (this.pingInterval) {
            clearInterval(this.pingInterval);
            this.pingInterval = undefined;
        }
    }

    /**
     * Attempt to reconnect after disconnect
     */
    protected attemptReconnect(): void {
        if (this.reconnectAttempts >= this.maxReconnectAttempts) {
            console.error('Max reconnect attempts reached');
            return;
        }

        this.reconnectAttempts++;
        const delay = this.reconnectDelay * Math.pow(2, this.reconnectAttempts - 1);

        setTimeout(() => {
            console.log(`Attempting to reconnect (${this.reconnectAttempts}/${this.maxReconnectAttempts})...`);
            this.connect(this.connectionId).catch(() => {
                // Will trigger another reconnect attempt via onclose
            });
        }, delay);
    }

    /**
     * Dispose resources
     */
    dispose(): void {
        this.disconnect();
        this.onConnectedEmitter.dispose();
        this.onDisconnectedEmitter.dispose();
        this.onMessageEmitter.dispose();
        this.onErrorEmitter.dispose();
        this.onExperimentEventEmitter.dispose();
        this.onArtifactEventEmitter.dispose();
        this.onSessionEventEmitter.dispose();
        this.onRunLogEmitter.dispose();
        this.onNotificationEmitter.dispose();
    }
}

