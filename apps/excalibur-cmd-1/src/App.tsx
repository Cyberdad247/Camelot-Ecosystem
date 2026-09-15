import { useEffect, useState, lazy, Suspense } from 'react';
import { TelemetryHeader } from './components/TelemetryHeader';
import { NodeInventory } from './components/NodeInventory';
import { HolographicGlobe } from './components/HolographicGlobe';
import { SovereignActions } from './components/SovereignActions';
import { AlfredDock } from './components/AlfredDock';
import { ExcaliburAuthCartridge } from './components/ExcaliburAuthCartridge';
import { OnboardingFlow } from './components/auth/OnboardingFlow';
import { DesktopGrid } from './components/dashboard/DesktopGrid';
import { TenantCarousel } from './components/TenantCarousel';
import { CartridgeLoadingFallback } from './components/CartridgeLoadingFallback';
import { ErrorBoundary } from './components/ErrorBoundary';
import { useEcosystemStore } from './state/useEcosystemStore';
import { NodeRecord, TelemetryData, CartridgeId } from './types';
import { Smartphone, Shield } from 'lucide-react';

// Dynamic Code Splitting for Tenant Carousel Cartridges (Lightweight Initial Load & Strict 4GB Boundary)
const KbaExecutiveCartridge = lazy(() =>
  import('./components/cartridges/KbaExecutiveCartridge').then(m => ({ default: m.KbaExecutiveCartridge }))
);
const DigitalFactoryCartridge = lazy(() =>
  import('./components/cartridges/DigitalFactoryCartridge').then(m => ({ default: m.DigitalFactoryCartridge }))
);
const OneVizionRecordsCartridge = lazy(() =>
  import('./components/cartridges/OneVizionRecordsCartridge').then(m => ({ default: m.OneVizionRecordsCartridge }))
);

export default function App() {
  const [nodes, setNodes] = useState<NodeRecord[]>([]);
  const [selectedNodeId, setSelectedNodeId] = useState<string | null>(null);
  const [telemetry, setTelemetry] = useState<TelemetryData | null>(null);

  // Authentication & Cartridge Hierarchy State
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [authMode, setAuthMode] = useState<'excalibur' | 'onboarding'>('onboarding');
  const [activeLeaseId, setActiveLeaseId] = useState<string | null>(null);
  const [operator, setOperator] = useState('VaShawn O. Head (Vizion)');
  const [activeCartridge, setActiveCartridge] = useState<CartridgeId>('ecosystem-pwa');

  const { deviceMode } = useEcosystemStore();

  useEffect(() => {
    // Fetch initial node registry
    fetch('/api/nodes')
      .then(res => res.json())
      .then(data => {
        setNodes(data);
        if (data.length > 0) {
          setSelectedNodeId(data[0].id);
        }
      })
      .catch(err => console.error('Failed to load registry:', err));

    // Connect telemetry stream (SSE)
    const eventSource = new EventSource('/api/telemetry');
    eventSource.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        setTelemetry(data);
      } catch (e) {
        console.error('Telemetry parse error:', e);
      }
    };

    return () => eventSource.close();
  }, []);

  const handleAuthenticated = (leaseId: string, opName: string) => {
    setActiveLeaseId(leaseId);
    setOperator(opName);
    setIsAuthenticated(true);
    setActiveCartridge('excalibur-ecc');
  };

  const handleLockVault = async () => {
    try {
      if (activeLeaseId) {
        await fetch('/api/auth/seal', {
          method: 'POST',
          headers: {
            'X-Camelot-Lease-ID': activeLeaseId
          }
        });
      }
    } catch (e) {
      console.error('Error locking vault:', e);
    }
    setIsAuthenticated(false);
    setActiveLeaseId(null);
  };

  const handleNodeAction = async (id: string, action: string) => {
    try {
      const res = await fetch(`/api/nodes/${id}/action`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-Camelot-Lease-ID': activeLeaseId || 'EXCALIBUR_LEASE_SOVEREIGN_V1000'
        },
        body: JSON.stringify({ action })
      });
      if (!res.ok) throw new Error('Action failed');
      const { node } = await res.json();
      
      // Update local state
      setNodes(prev => prev.map(n => n.id === id ? node : n));
    } catch (err) {
      console.error(err);
      alert('Sovereign action failed to execute. Check lease validity.');
    }
  };

  const selectedNode = nodes.find(n => n.id === selectedNodeId) || null;

  return (
    <div className="flex flex-col h-screen w-screen overflow-hidden bg-[#050510] text-[#F1EFF4] font-['Spectral'] selection:bg-[#D4AF37] selection:text-black">
      <TelemetryHeader telemetry={telemetry} />
      
      {!isAuthenticated ? (
        /* Vault Door: Cartridge 00 Excalibur Sovereign Bio-Auth Gate & Onboarding Flow */
        <main className="flex-1 overflow-y-auto flex flex-col">
          <div className="w-full bg-black/60 border-b border-[#4B0082]/60 px-4 py-2 flex items-center justify-center gap-3">
            <button
              type="button"
              onClick={() => setAuthMode('onboarding')}
              className={`px-3 py-1.5 rounded text-xs font-['Cinzel'] font-bold flex items-center gap-1.5 transition-all ${
                authMode === 'onboarding'
                  ? 'bg-[#D4AF37] text-black shadow-[0_0_15px_rgba(212,175,55,0.4)]'
                  : 'text-[#F1EFF4]/70 hover:text-[#D4AF37] border border-[#4B0082]/50'
              }`}
            >
              <Smartphone className="w-3.5 h-3.5" />
              <span>CAMELOT PWA ONBOARDING (S26)</span>
            </button>
            <button
              type="button"
              onClick={() => setAuthMode('excalibur')}
              className={`px-3 py-1.5 rounded text-xs font-['Cinzel'] font-bold flex items-center gap-1.5 transition-all ${
                authMode === 'excalibur'
                  ? 'bg-[#D4AF37] text-black shadow-[0_0_15px_rgba(212,175,55,0.4)]'
                  : 'text-[#F1EFF4]/70 hover:text-[#D4AF37] border border-[#4B0082]/50'
              }`}
            >
              <Shield className="w-3.5 h-3.5" />
              <span>EXCALIBUR 3-PILL CHAMBER</span>
            </button>
          </div>

          <div className="flex-1 flex items-center justify-center p-2 sm:p-4">
            {authMode === 'onboarding' ? (
              <OnboardingFlow
                onComplete={() =>
                  handleAuthenticated('EXCALIBUR_ED25519_LEASE_ACTIVE', 'VaShawn O. Head (Vizion)')
                }
              />
            ) : (
              <ExcaliburAuthCartridge onAuthenticated={handleAuthenticated} />
            )}
          </div>
        </main>
      ) : (
        /* Authenticated: Tenant Carousel + Mounted Cartridges */
        <div className="flex-1 flex flex-col overflow-hidden">
          <TenantCarousel
            activeCartridge={activeCartridge}
            onSelectCartridge={setActiveCartridge}
            onLockVault={handleLockVault}
            leaseId={activeLeaseId}
            operator={operator}
          />

          <main className="flex-1 overflow-hidden relative">
            {activeCartridge === 'ecosystem-pwa' && (
              <ErrorBoundary
                cartridgeName="Camelot Ecosystem PWA (S26 Edge Shell)"
                onReset={() => setActiveCartridge('excalibur-ecc')}
              >
                <div
                  className={`h-full overflow-y-auto p-2 sm:p-4 md:p-6 pb-20 ${
                    deviceMode === 'mobile_s26'
                      ? 'max-w-[480px] mx-auto border-x border-[#4B0082]/60 shadow-[0_0_50px_rgba(75,0,130,0.4)] bg-[#050510]/95 min-h-full'
                      : 'max-w-[1600px] mx-auto'
                  }`}
                >
                  <DesktopGrid />
                </div>
              </ErrorBoundary>
            )}

            {activeCartridge === 'excalibur-ecc' && (
              <div className="h-full p-2 sm:p-4 md:p-6 lg:p-8 overflow-hidden">
                <div className="h-full max-w-[1600px] mx-auto grid grid-cols-1 lg:grid-cols-12 gap-4 sm:gap-6 relative">
                  
                  {/* Glass 1: Blueprint OS / Node Inventory */}
                  <div className="hidden md:block lg:col-span-3 h-full">
                    <NodeInventory 
                      nodes={nodes} 
                      selectedId={selectedNodeId} 
                      onSelect={setSelectedNodeId} 
                    />
                  </div>

                  {/* Glass 2: Holographic Globe (Main Canvas) */}
                  <div className="col-span-1 lg:col-span-6 h-full min-h-[40vh] flex flex-col relative">
                    {/* Mobile node selector overlay */}
                    <div className="md:hidden absolute top-4 left-4 right-4 z-20">
                      <select 
                        className="w-full bg-[#121217]/90 border border-[#9D4EDD]/40 text-[#F0EAD6] p-3 rounded-lg font-mono text-xs focus:outline-none focus:border-[#E5B842] min-h-[44px]"
                        value={selectedNodeId || ''}
                        onChange={(e) => setSelectedNodeId(e.target.value)}
                      >
                        <option value="" disabled>SELECT A NODE</option>
                        {nodes.map(n => (
                          <option key={n.id} value={n.id}>{n.name} [{n.status}]</option>
                        ))}
                      </select>
                    </div>
                    <HolographicGlobe />
                  </div>

                  {/* Glass 3: Sovereign Actions */}
                  <div className="lg:col-span-3 h-1/2 lg:h-full">
                    <SovereignActions 
                      node={selectedNode} 
                      onAction={handleNodeAction} 
                    />
                  </div>
                  
                </div>
              </div>
            )}

            {activeCartridge === 'kba-executive' && (
              <ErrorBoundary
                cartridgeName="KBA Executive (Cartridge 01)"
                onReset={() => setActiveCartridge('excalibur-ecc')}
              >
                <Suspense fallback={<CartridgeLoadingFallback cartridgeName="KBA Executive (Cartridge 01)" />}>
                  <KbaExecutiveCartridge />
                </Suspense>
              </ErrorBoundary>
            )}
            {activeCartridge === 'digital-factory' && (
              <ErrorBoundary
                cartridgeName="Digital Factory (Cartridge 02)"
                onReset={() => setActiveCartridge('excalibur-ecc')}
              >
                <Suspense fallback={<CartridgeLoadingFallback cartridgeName="Digital Factory (Cartridge 02)" />}>
                  <DigitalFactoryCartridge />
                </Suspense>
              </ErrorBoundary>
            )}
            {activeCartridge === '1vizion-rcrds' && (
              <ErrorBoundary
                cartridgeName="1VIZION RCRDS (Cartridge 03)"
                onReset={() => setActiveCartridge('excalibur-ecc')}
              >
                <Suspense fallback={<CartridgeLoadingFallback cartridgeName="1VIZION RCRDS (Cartridge 03)" />}>
                  <OneVizionRecordsCartridge />
                </Suspense>
              </ErrorBoundary>
            )}
          </main>

          {/* Alfred Audio Engine Dock */}
          {(activeCartridge === 'excalibur-ecc' || activeCartridge === 'ecosystem-pwa') && <AlfredDock />}
        </div>
      )}
    </div>
  );
}
