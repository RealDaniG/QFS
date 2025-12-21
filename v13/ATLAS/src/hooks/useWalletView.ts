'use client';

import { useCallback, useEffect, useMemo, useState } from 'react';
import { useAuth } from './useAuth';
import { atlasFetch } from '../lib/api';

export interface WalletResponse {
  wallet_id: string;
  owner_id: string;
  name: string;
  description?: string | null;
  asset: string;
  created_at: string;
  updated_at: string;
  is_active: boolean;
  balances: Array<{ asset: string; balance: number; locked: number; total: number }>;
}

export function useWalletView() {
  const { did } = useAuth();

  const [wallets, setWallets] = useState<WalletResponse[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  const refresh = useCallback(async () => {
    setIsLoading(true);
    try {
      const res = await atlasFetch('/api/v1/wallets/', {
        method: 'GET',
      });

      if (!res.ok) {
        throw new Error(`Failed to fetch wallets: ${res.status}`);
      }

      const data = (await res.json()) as WalletResponse[];
      setWallets(Array.isArray(data) ? data : []);
      setError(null);
    } catch (e) {
      setError(e as Error);
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    refresh();
  }, [refresh]);

  const walletSummary = useMemo(() => {
    // UI-safe read-only summary (no mutation): pick the first wallet.
    const w = wallets[0];
    if (!w) {
      return null;
    }

    const qfs = w.balances.find((b) => b.asset === 'QFS') || null;
    return {
      did,
      wallet_id: w.wallet_id,
      owner_id: w.owner_id,
      qfs,
    };
  }, [did, wallets]);

  return {
    wallets,
    walletSummary,
    isLoading,
    error,
    refresh,
  };
}
