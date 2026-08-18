import { Card } from '@/components/ui/Card';
import React, { Component, type ErrorInfo, type ReactNode } from 'react';

interface Props {
  children: ReactNode;
}

interface State {
  hasError: boolean;
  error: Error | null;
}

export class ErrorBoundary extends Component<Props, State> {
  public state: State = {
    hasError: false,
    error: null,
  };

  public static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error };
  }

  public componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    console.error('Uncaught error:', error, errorInfo);
  }

  public render() {
    if (this.state.hasError) {
      return (
        <div className="h-screen w-full flex items-center justify-center bg-black">
          <Card className="bg-red-950 border-red-800 text-white" title="System Failure">
            <p>The Quantum Engine encountered a critical fault.</p>
            <pre className="mt-4 p-2 bg-black/50 rounded text-xs text-red-300 overflow-auto">
              {this.state.error?.message}
            </pre>
            <button
              onClick={() => window.location.reload()}
              className="mt-4 px-4 py-2 bg-red-600 rounded hover:bg-red-700"
            >
              Reboot System
            </button>
          </Card>
        </div>
      );
    }

    return this.props.children;
  }
}
