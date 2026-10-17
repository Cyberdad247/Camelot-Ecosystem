export interface CloudroomSessionConfig {
  sessionId: string;
  agentCommand: string;
  workdir: string;
  maxMemoryMb?: number;
  environment?: Record<string, string>;
}

export interface CloudroomStatus {
  sessionId: string;
  running: boolean;
  pid?: number;
  cpuPercent?: number;
  memoryMb?: number;
}

export class CloudroomBridgeClient {
  private endpoint: string;

  constructor(endpoint = 'http://100.110.180.18:8420') {
    this.endpoint = endpoint;
  }

  public getSessionUrl(sessionId: string): string {
    return `${this.endpoint}/api/v1/sessions/${encodeURIComponent(sessionId)}`;
  }

  public createSessionPayload(config: CloudroomSessionConfig): Record<string, unknown> {
    return {
      session_id: config.sessionId,
      command: config.agentCommand,
      cwd: config.workdir,
      limits: {
        max_ram_mb: config.maxMemoryMb || 1024,
      },
      env: config.environment || {},
      created_at: new Date().toISOString(),
    };
  }
}
