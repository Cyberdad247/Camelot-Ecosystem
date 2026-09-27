export class AionTimelineCache {
  private frames: any[] = [];
  private limit: number;

  constructor(limit = 20) {
    this.limit = limit;
  }

  public push(state: any) {
    this.frames.push({
      ...state,
      timestamp: Date.now(),
    });
    if (this.frames.length > this.limit) {
      this.frames.shift();
    }
  }

  public getHistory() {
    return this.frames;
  }

  public getFrame(index: number) {
    if (index >= 0 && index < this.frames.length) {
      return this.frames[index];
    }
    return null;
  }
}
