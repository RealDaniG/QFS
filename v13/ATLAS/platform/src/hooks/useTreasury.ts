'use client';

import { useState, useEffect, useCallback } from 'react';
import { getTreasury, TreasuryEngine, TokenAccount, TransactionRecord } from '@/lib/economics/treasury-engine';
import { useAuth } from './useAuth';

export function useTreasury() {
    const { did } = useAuth();
    const [balance, setBalance] = useState<TokenAccount | null>(null);
    const [history, setHistory] = useState<TransactionRecord[]>([]);
    const [isLoading, setIsLoading] = useState(true);

    const refresh = useCallback(() => {
        if (!did) return;

        const treasury = getTreasury();
        const acct = treasury.getBalance(did);
        const txs = treasury.getHistory(did);

        setBalance({ ...acct }); // Clone to trigger update if needed
        setHistory([...txs]);
        setIsLoading(false);
    }, [did]);

    useEffect(() => {
        if (!did) return;

        // Initial load
        refresh();

        // Poll for updates (simple reactivity for simulation)
        const interval = setInterval(refresh, 2000);
        return () => clearInterval(interval);
    }, [did, refresh]);

    return {
        balance,
        history,
        isLoading,
        refresh
    };
}
