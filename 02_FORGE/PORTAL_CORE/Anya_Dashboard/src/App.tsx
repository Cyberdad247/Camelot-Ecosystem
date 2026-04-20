import React from 'react';
import { BrowserRouter, Routes, Route, Navigate, Outlet } from 'react-router-dom';
import AnyasLink from './features/brain/AnyasLink';
import BrainInterface from './features/brain/BrainInterface';
import MorphingHUD from './features/brain/MorphingHUD';
import SwarmMonitor from './features/swarm/SwarmMonitor';
import BottomNav from './components/ui/BottomNav';
import { ErrorBoundary } from '@/components/ui/ErrorBoundary';

// Configuration
// NOTE: This is the "Visual Context" for the Voice Agent.
// Currently set to Wikipedia as a placeholder for "Research Mode".
const ANYA_EXTERNAL_URL = "https://en.m.wikipedia.org/wiki/Special:Random"; 

function Layout() {
  return (
    <div className="flex flex-col h-screen bg-black text-white overflow-hidden">
      <main className="flex-1 overflow-hidden"> 
        <Outlet />
      </main>
      <div className="fixed bottom-0 left-0 right-0 z-50">
        <BottomNav />
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
            <Route path="/anyas-link" element={<AnyasLink externalUrl={ANYA_EXTERNAL_URL} />} />
            <Route path="/brain" element={<MorphingHUD />} />
            <Route path="/legacy-brain" element={<BrainInterface />} />
            <Route path="/swarm" element={<SwarmMonitor />} />
            <Route path="/" element={<Navigate to="/anyas-link" replace />} />
          </Route>
        </Routes>
      </BrowserRouter>
    </ErrorBoundary>
  );
}
