import React, { Suspense, lazy } from 'react';
import { BrowserRouter, Routes, Route, Navigate, Outlet } from 'react-router-dom';
import BottomNav from './components/ui/BottomNav';
import { ErrorBoundary } from '@/components/ui/ErrorBoundary';
import { runtimeConfig } from '@/config/runtime';

const AnyasLink = lazy(() => import('./features/brain/AnyasLink'));
const BrainInterface = lazy(() => import('./features/brain/BrainInterface'));
const MorphingHUD = lazy(() => import('./features/brain/MorphingHUD'));
const OpenVikingDashboard = lazy(() => import('./features/openviking/OpenVikingDashboard'));
const SwarmMonitor = lazy(() => import('./features/swarm/SwarmMonitor'));

function Layout() {
  return (
    <div className="flex h-dvh flex-col overflow-hidden bg-black text-white">
      <main className="min-h-0 flex-1 overflow-hidden"> 
        <Suspense fallback={<RouteLoading />}>
          <Outlet />
        </Suspense>
      </main>
      <BottomNav />
    </div>
  );
}

function RouteLoading() {
  return (
    <div className="grid h-full place-items-center bg-[#050208] text-slate-100">
      <div className="rounded-3xl border border-fuchsia-300/20 bg-black/60 px-8 py-6 text-center shadow-2xl shadow-fuchsia-950/30">
        <p className="text-xs font-black uppercase tracking-[0.28em] text-fuchsia-200">Camelot-OS</p>
        <p className="mt-2 text-lg font-black">Loading command deck...</p>
      </div>
    </div>
  );
}

export default function App() {
  return (
    <ErrorBoundary>
      <BrowserRouter>
        <Routes>
          <Route element={<Layout />}>
            <Route path="/anyas-link" element={<AnyasLink externalUrl={runtimeConfig.visualContextUrl} />} />
            <Route path="/brain" element={<MorphingHUD />} />
            <Route path="/openviking" element={<OpenVikingDashboard />} />
            <Route path="/legacy-brain" element={<BrainInterface />} />
            <Route path="/swarm" element={<SwarmMonitor />} />
            <Route path="/" element={<Navigate to={runtimeConfig.appHomeRoute} replace />} />
          </Route>
        </Routes>
      </BrowserRouter>
    </ErrorBoundary>
  );
}
