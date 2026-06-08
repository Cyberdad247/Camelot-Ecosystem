import { create } from 'zustand';

export type BridgeStatus = 'idle' | 'connecting' | 'connected' | 'error';

export interface AnyaCodecState {
  bridgeStatus: BridgeStatus;
  lastMessage: string;
  setBridgeStatus: (status: BridgeStatus) => void;
  setLastMessage: (message: string) => void;
}

export const useAnyaCodecStore = create<AnyaCodecState>((set) => ({
  bridgeStatus: 'idle',
  lastMessage: '',
  setBridgeStatus: (bridgeStatus) => set({ bridgeStatus }),
  setLastMessage: (lastMessage) => set({ lastMessage }),
}));
