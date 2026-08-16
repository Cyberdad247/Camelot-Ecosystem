import AppShell from '@/components/layout/AppShell';
import { ErrorBoundary } from '@/components/ui/ErrorBoundary';
import React, { Suspense, lazy } from 'react';
import { BrowserRouter, Navigate, Route, Routes } from 'react-router-dom';
import FactoryDashboard from './features/agency/FactoryDashboard';

// Core feature pages
const SystemHub = lazy(() => import('./features/hub/SystemHub'));
const CamelotOsCommand = lazy(() => import('./features/camelot-os/CamelotOsCommand'));
const AlexTaskManager = lazy(() => import('./features/alex/AlexTaskManager'));
const ResearchDepartment = lazy(() => import('./features/research/ResearchDepartment'));
const CartridgeDeck = lazy(() => import('./features/cartridges/CartridgeDeck'));
const KnightIntake = lazy(() => import('./features/onboarding/KnightIntake'));
const DefenseGridConsole = lazy(() => import('./features/defense-grid/DefenseGridConsole'));

// Legacy / system pages
const OpenVikingDashboard = lazy(() => import('./features/openviking/OpenVikingDashboard'));
const SwarmMonitor = lazy(() => import('./features/swarm/SwarmMonitor'));
const AnyasLink = lazy(() => import('./features/brain/AnyasLink'));
const MorphingHUD = lazy(() => import('./features/brain/MorphingHUD'));
const BrainInterface = lazy(() => import('./features/brain/BrainInterface'));
const SupportPortal = lazy(() => import('./features/support/SupportPortal'));

function RouteLoading() {
  return (
    <div className="grid h-full place-items-center bg-[#050208] text-slate-100">
      <div className="rounded-3xl border border-fuchsia-300/20 bg-black/60 px-8 py-6 text-center shadow-2xl shadow-fuchsia-950/30">
        <p className="text-xs font-black uppercase tracking-[0.28em] text-fuchsia-200">
          Camelot-OS
        </p>
        <p className="mt-2 text-lg font-black">Loading command deck…</p>
      </div>
    </div>
  );
}

export default function App() {
  return (
    <ErrorBoundary>
      <BrowserRouter>
        <Suspense fallback={<RouteLoading />}>
          <Routes>
            <Route element={<AppShell />}>
              {/* Primary */}
              <Route path="/" element={<SystemHub />} />
              <Route path="/camelot-os" element={<CamelotOsCommand />} />
              <Route path="/alex" element={<AlexTaskManager />} />
              <Route path="/research" element={<ResearchDepartment />} />
              <Route path="/dev" element={<FactoryDashboard />} />
              <Route path="/defense-grid" element={<DefenseGridConsole />} />
              <Route path="/onboarding" element={<KnightIntake />} />
              <Route path="/cartridge/:id" element={<CartridgeDeck />} />

              {/* System */}
              <Route path="/openviking" element={<OpenVikingDashboard />} />
              <Route path="/swarm" element={<SwarmMonitor />} />
              <Route
                path="/anyas-link"
                element={<AnyasLink externalUrl="https://en.m.wikipedia.org/wiki/Special:Random" />}
              />

              {/* Legacy */}
              <Route path="/brain" element={<MorphingHUD />} />
              <Route path="/legacy-brain" element={<BrainInterface />} />
              <Route path="/support/:sessionId" element={<SupportPortal />} />

              {/* Catch-all */}
              <Route path="*" element={<Navigate to="/" replace />} />
            </Route>
          </Routes>
        </Suspense>
      </BrowserRouter>
    </ErrorBoundary>
  );
}
