/**
 * Observer: A lightweight reactive state container.
 * Inspired by @playcanvas/observer.
 */
export class Observer {
  constructor(initialState = {}) {
    this._state = initialState;
    this._listeners = new Set();
  }

  get state() {
    return this._state;
  }

  /**
   * Set one or more properties. Triggers updates.
   */
  set(patch) {
    this._state = { ...this._state, ...patch };
    this.notify();
  }

  /**
   * Subscribe to changes.
   */
  subscribe(callback) {
    this._listeners.add(callback);
    // Initial sync
    callback(this._state);
    return () => this._listeners.delete(callback);
  }

  notify() {
    this._listeners.forEach((callback) => callback(this._state));
  }
}
