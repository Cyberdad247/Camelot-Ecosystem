// Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.
// Camelot Apex OS — CONFIDENTIAL AND PROPRIETARY
import { create } from 'zustand';

interface Object3D {
  id: string;
  type: 'cube' | 'sphere' | 'model';
  position: [number, number, number];
  color: string;
}

interface EngineState {
  objects: Object3D[];
  addObject: (obj: Object3D) => void;
  clearScene: () => void;
}

export const useEngineStore = create<EngineState>((set) => ({
  objects: [],
  addObject: (obj) => set((state) => ({ objects: [...state.objects, obj] })),
  clearScene: () => set({ objects: [] }),
}));