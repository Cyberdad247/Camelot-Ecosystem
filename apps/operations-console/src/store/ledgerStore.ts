import { useState, useEffect } from 'react';

export interface CRDTEntry {
  account_id: string;
  entry_type: 'Debit' | 'Credit';
  amount_cents: number;
}

export interface CRDTTransaction {
  id: string;
  tenant_id: string;
  timestamp: number;
  entries: CRDTEntry[];
  description: string;
  synced: boolean;
}

// Global in-memory pub/sub state for zero-dependency brutalist CRDT store
let globalPendingTransactions: CRDTTransaction[] = [
  {
    id: 'tx_init_001',
    tenant_id: 'KBA-TENANT-001',
    timestamp: Date.now() - 60000,
    description: 'Initial Sovereign Capital Deposit',
    entries: [
      { account_id: 'ACC_REVENUE_01', entry_type: 'Debit', amount_cents: 15000 },
      { account_id: 'ACC_REFUNDS_01', entry_type: 'Credit', amount_cents: 15000 },
    ],
    synced: false,
  },
];

const listeners = new Set<() => void>();

function notifyListeners() {
  listeners.forEach((listener) => listener());
}

export function addTransaction(transaction: Omit<CRDTTransaction, 'id' | 'timestamp' | 'synced'>) {
  const newTx: CRDTTransaction = {
    ...transaction,
    id: `tx_${Date.now()}_${Math.random().toString(36).substring(2, 7)}`,
    timestamp: Date.now(),
    synced: false,
  };

  globalPendingTransactions = [newTx, ...globalPendingTransactions];
  notifyListeners();
  return newTx;
}

export function clearSyncedTransactions(ids: string[]) {
  globalPendingTransactions = globalPendingTransactions.filter((tx) => !ids.includes(tx.id));
  notifyListeners();
}

export function useLedgerStore() {
  const [pendingTransactions, setPendingTransactions] = useState<CRDTTransaction[]>(globalPendingTransactions);

  useEffect(() => {
    const handleChange = () => {
      setPendingTransactions([...globalPendingTransactions]);
    };

    listeners.add(handleChange);
    return () => {
      listeners.delete(handleChange);
    };
  }, []);

  return {
    pendingTransactions,
    addTransaction,
    clearSyncedTransactions,
    offlineItemCount: pendingTransactions.length,
  };
}
