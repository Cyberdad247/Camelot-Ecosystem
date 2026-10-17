export class PiMonoRenderer {
  public onRender?: (output: string) => void;
  private buffer = '';
  private timeout: NodeJS.Timeout | null = null;
  public static readonly LATENCY_CAP_MS = 200;

  public updateFrame(data: string): void {
    this.buffer += data;
    if (!this.timeout) {
      this.timeout = setTimeout(() => {
        this.render();
      }, PiMonoRenderer.LATENCY_CAP_MS);
    }
  }

  public flush(): void {
    if (this.timeout) {
      clearTimeout(this.timeout);
      this.timeout = null;
    }
    this.render();
  }

  private render(): void {
    if (this.onRender && this.buffer.length > 0) {
      this.onRender(this.buffer);
    }
    this.buffer = '';
    this.timeout = null;
  }
}
