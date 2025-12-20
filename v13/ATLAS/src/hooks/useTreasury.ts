'use client';

import { useState, useEffect, useCallback } from 'react';
import { getTreasury, TokenAccount, TransactionRecord } from '@/lib/economics/treasury-engine';
import { useWalletAuth } from './useWalletAuth';

export function useTreasury() {
    const { address: walletAddress, isConnected } = useWalletAuth();
    const [balance, setBalance] = useState<TokenAccount | null>(null);
    const [history, setHistory] = useState<TransactionRecord[]>([]);
    const [isLoading, setIsLoading] = useState(true);

    const refresh = useCallback(async () => {
        // We can always show data for the connected user or a default
        const identifier = walletAddress || 'demo_user';

        try {
            const treasury = getTreasury();
            // treasury is an instance of TreasuryService

            const [acct, txs] = await Promise.all([
                treasury.getBalance(identifier),
                treasury.getHistory(identifier)
            ]);

            setBalance(acct);
            setHistory(txs);
        } catch (e) {
            console.error("Failed to refresh treasury in useTreasury hook:", e);
        } finally {
            setIsLoading(false);
        }
    }, [walletAddress]);

    useEffect(() => {
        refresh();
        const interval = setInterval(refresh, 60000); // 60s poll for treasury
        return () => clearInterval(interval);
    }, [refresh]);

    return {
        balance,
        history,
        isLoading,
        refresh
    };
}
