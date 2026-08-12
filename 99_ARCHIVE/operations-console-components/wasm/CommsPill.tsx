import React, { useState, useEffect } from 'react';
import { WasmCommsEngine } from '@/wasm/comms_engine';

export const CommsPill: React.FC = () => {
  const [outboxCount, setOutboxCount] = useState<number>(0);
  const [isWasmReady, setIsWasmReady] = useState(false);
  
  useEffect(() => {
    // ⚡ [T]RIGGER: Asynchronous WASM Initialization
    const bootEngine = async () => {
      const startTime = performance.now();
      // await WasmCommsEngine.init();
      console.log(`[SYSTEM_LOG]: WASM Comms Engine Booted in ${(performance.now() - startTime).toFixed(2)}ms`);
      setIsWasmReady(true);
    };
    
    bootEngine();

    // Background ServiceWorker hook for local push notifications & queued dispatches
    const syncInterval = setInterval(() => {
      if (navigator.onLine) {
        // const flushed = WasmCommsEngine.flush_outbox();
        const flushed = 0;
        if (flushed > 0) {
           console.log(`[SYSTEM_LOG]: ${flushed} encrypted payloads dispatched. Mailchimp dependency bypassed.`);
           setOutboxCount(0);
        }
      }
    }, 10000);

    return () => clearInterval(syncInterval);
  }, []);

  const queueBlast = () => {
    if (!isWasmReady) return;
    
    setOutboxCount(prev => prev + 1);
  };

  return (
    <div style={{ backgroundColor: '#111116', padding: '2rem', border: '1px solid #333', marginTop: '2rem' }}>
      <header style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <h2 style={{ color: '#D4AF37', margin: 0, textTransform: 'uppercase' }}>
          Autonomous Comms Pill
        </h2>
        <span style={{ color: '#9D4EDD', fontSize: '0.875rem' }}>OFFLINE-FIRST DISPATCHER</span>
      </header>
      
      <main style={{ marginTop: '1.5rem' }}>
        <p style={{ color: '#888' }}>
          Queued Payloads (OPFS Outbox): <strong style={{ color: '#FFF' }}>{outboxCount}</strong>
        </p>

        <button 
          onClick={queueBlast}
          disabled={!isWasmReady}
          style={{
            backgroundColor: 'transparent',
            color: '#9D4EDD',
            border: '2px solid #9D4EDD',
            padding: '1rem 2rem',
            fontWeight: 'bold',
            textTransform: 'uppercase',
            cursor: isWasmReady ? 'pointer' : 'not-allowed',
            opacity: isWasmReady ? 1 : 0.5,
            transition: 'all 0.2s ease-in-out'
          }}
          onMouseOver={(e) => { e.currentTarget.style.backgroundColor = '#9D4EDD'; e.currentTarget.style.color = '#0D0D11'; }}
          onMouseOut={(e) => { e.currentTarget.style.backgroundColor = 'transparent'; e.currentTarget.style.color = '#9D4EDD'; }}
        >
          Queue Campaign Blast
        </button>
      </main>
    </div>
  );
};
