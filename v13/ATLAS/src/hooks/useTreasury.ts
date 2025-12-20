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
        // Auth Guard: Don't fetch if not connected
        if (!isConnected || !walletAddress) {
            setIsLoading(false);
            return;
        }

        try {
            const treasury = getTreasury();
            // treasury is an instance of TreasuryService

            const [acct, txs] = await Promise.all([
                treasury.getBalance(walletAddress),
                treasury.getHistory(walletAddress)
            ]);

            setBalance(acct);
            setHistory(txs);
        } catch (e) {
            console.error("Failed to refresh treasury in useTreasury hook:", e);
        } finally {
            setIsLoading(false);
        }
    }, [walletAddress, isConnected]);

    useEffect(() => {
        // Only fetch when connected
        if (!isConnected) {
            setIsLoading(false);
            return;
        }

        refresh();
        const interval = setInterval(refresh, 60000); // 60s poll for treasury
        return () => clearInterval(interval);
    }, [refresh, isConnected]);

    return {
        balance,
        history,
        isLoading,
        refresh
    };
}
