'use client';

import { useState, useEffect, useCallback } from 'react';
import { atlasFetch } from '../lib/api';
import { useWalletAuth } from './useWalletAuth';

export interface TokenAccount {
    balance: number;
    rewards: number;
    staked: number;
    currency: string;
    reputation: number;
    reputation_breakdown?: {
        content_quality: number;
        engagement: number;
        governance: number;
    };
}

export interface TransactionRecord {
    id: string;
    type: string;
    reason: string;
    amount: number;
    timestamp: number;
    ref?: string;
}

export function useTreasury() {
    const { address: walletAddress, isConnected, sessionToken } = useWalletAuth();
    const [balance, setBalance] = useState<TokenAccount | null>(null);
    const [history, setHistory] = useState<TransactionRecord[]>([]);
    const [isLoading, setIsLoading] = useState(true);

    const refresh = useCallback(async () => {
        // Auth Guard: Don't fetch if not connected or no session
        if (!isConnected || !walletAddress || !sessionToken) {
            setIsLoading(false);
            return;
        }

        const baseUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

        try {
            const [balanceRes, historyRes] = await Promise.all([
                fetch(`${baseUrl}/api/wallet/balance`, {
                    headers: { 'Authorization': `Bearer ${sessionToken}` }
                }),
                fetch(`${baseUrl}/api/wallet/transactions`, {
                    headers: { 'Authorization': `Bearer ${sessionToken}` }
                })
            ]);

            if (balanceRes.ok && historyRes.ok) {
                const balanceData = await balanceRes.json();
                const historyData = await historyRes.json();

                // Adapter for new API shape
                setBalance({
                    balance: balanceData.balance.FLX,
                    rewards: 0,
                    staked: 0,
                    currency: 'FLX',
                    reputation: 0,
                });

                // Adapter for new transactions
                setHistory(historyData.transactions.map((tx: any) => ({
                    id: tx.id,
                    type: tx.type,
                    reason: tx.description,
                    amount: tx.amount,
                    timestamp: tx.timestamp
                })));
            }
        } catch (e) {
            console.error("Failed to refresh treasury in useTreasury hook:", e);
        } finally {
            setIsLoading(false);
        }
    }, [walletAddress, isConnected, sessionToken]);

    useEffect(() => {
        if (!isConnected || !sessionToken) {
            setIsLoading(false);
            setBalance(null);
            setHistory([]);
            return;
        }

        refresh();
        const interval = setInterval(refresh, 30000);
        return () => clearInterval(interval);
    }, [refresh, isConnected, sessionToken]);

    return {
        balance,
        history,
        isLoading,
        refresh
    };
}
